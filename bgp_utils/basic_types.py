"""
This file defines some basic types of BGP implementation. 
"""

from enum import Enum
from abc import ABC, abstractmethod
import ipaddress
from binary_utils.utils import *

# TODO: Change this into all 
# TODO: Use `BinaryField` to unify all BGP fields. (Do we need that?)
# Currently you should not think this much!
class BinaryField(ABC):
    """
    The binary field.
    """
    @abstractmethod
    def get_binary_expression(self) -> bytes:
        """
        Get the binary expression of the field.
        """
        pass

    def get_binary_length(self):
        """
        Get the length of the field.
        """
        return len(self.get_binary_expression())

ASN_BYTE_NUM = 2
IP4_BYTE_NUM = 4

class IPType(Enum):
    """
    IP type
    """
    IPV4 = 1
    IPV6 = 2

ASN = int
ASPath = list[int]
ASSet = set[int]

class IP:
    """
    IP address
    """
    def __init__(self, ip_addr:str):
        if ':' in ip_addr:
            self.type = IPType.IPV6
            self.value = str(ipaddress.IPv6Address(ip_addr).exploded)
            self.segments = list(map(int, self.value.split(':')))
            assert len(self.segments)==8
        else:
            self.type = IPType.IPV4
            self.value = str(ipaddress.IPv4Address(ip_addr).exploded)
            self.segments = list(map(int, self.value.split('.')))
            assert len(self.segments)==4
    
    def get_str_expression(self):
        """
        Get the string expression of the IP address.
        """
        return self.value

class IPPrefix:
    """
    IP address
    """
    def __init__(self, prefix:str):
        assert('/' in prefix)
        original_addr, prefix_length = prefix.split('/')
        self.prefix_length : int = int(prefix_length)
        self.address : IP = IP(original_addr)
        self.type : IPType = self.address.type
        prefix_segment_len = 16 if self.type==IPType.IPV6 else 8
        self.prefix_segment_num : int = (self.prefix_length+prefix_segment_len-1) // prefix_segment_len
        # prefix segments are the rounded segments exactly covering the prefix
        self.prefix_segments = self.address.segments[:self.prefix_segment_num].copy()

    # To Check: are the trailing bits processed normally?
    # TODO: Should this method be implemented here or in other places?
    def get_binary_expression(self):
        """
        Get the binary expression of the IP prefix. 
        """
        return num2bytes(self.prefix_length,1) + b''.join(num2bytes(segment,1) for segment in self.prefix_segments)

    def get_str_expression(self):
        """
        Get the string expression of the IP prefix.
        """
        if self.type == IPType.IPV6:
            raise NotImplementedError("`get_str_expression` for IPv6 address has not been implemented!")
        return f"{self.address.get_str_expression()}/{self.prefix_length}"

class IPList(list[IP]):
    """
    A list of the IP addresses.
    """
    def __new__(cls, value):
        if not isinstance(value, list):
            raise ValueError("Wrong initialization of `IPList`: value not a list")
        ret_list  = []
        for item in value:
            if not isinstance(item, (IP,str)):
                raise ValueError(f"Wrong initialization of `IPList`: {item} not a legal type")
            if isinstance(item, str):
                item = IP(item)
            ret_list.append(item)
        return super().__new__(cls, ret_list)

class IPPrefixList(list[IPPrefix]):
    """
    A list of the IP prefixes.
    """
    def __new__(cls, value):
        if not isinstance(value, list):
            raise ValueError("Wrong initialization of `IPPrefixList`: value not a list")
        ret_list  = []
        for item in value:
            if not isinstance(item, (IPPrefix,str)):
                raise ValueError(f"Wrong initialization of `IPPrefixList`: {item} not a legal type")
            if isinstance(item, str):
                item = IPPrefix(item)
            ret_list.append(item)
        return super().__new__(cls, ret_list)

# TODO: is there any different binary expressions of the IP address?
def ip2bytes(ip: IP):
    """
    Convert IP into bytes
    """
    if ip.type==IPType.IPV6:
        # TODO
        raise ValueError("IP version IPv6 not supported in `ip2bytes`!")
    return b''.join(num2bytes(segment,1) for segment in ip.segments)
