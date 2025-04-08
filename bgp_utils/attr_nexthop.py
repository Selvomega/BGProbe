from data_utils.binary_utils import * 
from .attr_base import PathAttributeType, BaseAttr
from .basic_types import *

# TODO: How to deal with the length of expression of IP addresses?
class NextHopAttr(BaseAttr):
    """
    BGP path attribute: NEXT_HOP
    """
    def __init__(self, ip: IP):
        """
        Initialization
        """
        ###### Initializing the content part ######
        if ip.type == IPType.IPV6:
            # TODO
            raise ValueError("IP version IPv6 not supported in `NextHop`!")
        self.ip: IP = ip
        ###### Initializing the binary part ######
        super().__init__()
        ###### Set the binary part ######
        self.reset()
    
    def reset(self, **kwarg):
        """
        Reset the attribute into the original status.
        """
        self.attr_flag_b : bytes = self.set_attr_flag(attribute=self.get_type(), ext_len=1)
        self.attr_type_b : bytes = self.set_attr_type(attribute=self.get_type())
        # TODO: To deal with the IPv6 case.
        self.attr_len_b : bytes = num2bytes(IP4_BYTE_NUM,1)
        self.attr_value_b : bytes = ip2bytes(self.ip)

    def set_attr_value(self, **kwargs):
        """
        You can modify the `attr_value_b` of the attribute here.
        Two alternative ways of modifying the attribute value:
        1. ip: IP
        2. ip_str: str
        """
        if 'self_defined' in kwargs:
            self_defined = kwargs['self_defined']
            assert isinstance(self_defined, bytes)
            super().set_attr_value(self_defined)
            return
        elif 'ip' in kwargs:
            ip: IP = kwargs['ip']
            self.attr_value_b = ip2bytes(ip)
        elif 'ip_str' in kwargs:
            ip_str = kwargs['ip_str']
            ip: IP = IP(ip_str)
            self.attr_value_b = ip2bytes(ip)
        else:
            raise ValueError("Invalid input parameter!")

    def get_type(self):
        return PathAttributeType.NEXT_HOP

    def set_next_hop(self, ip:IP):
        """
        Set the ORIGIN type of this attribute.
        """
        if ip.type == IPType.IPV6:
            # TODO
            raise ValueError("IP version IPv6 not supported in `NextHop`!")
        self.ip = ip
    