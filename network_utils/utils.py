import os, ipaddress
from enum import Enum

########## Cloud VM utils ##########

def gcloud_get_instance_ip(instance_name, region="us-west2-b"):
    """
    Get the external IP of a gcloud instance with given instance name.
    When zone is NOT specified, we will use a default one.
    """
    cmd = f"gcloud compute instances describe {instance_name} --zone={region} --format=\"get(networkInterfaces[0].accessConfigs[0].natIP)\""
    external_ip = os.popen(cmd).read().strip()
    return external_ip

########## IP utils ##########

class IPType(Enum):
    """
    IP type
    """
    IPV4 = 1
    IPV6 = 2

def get_ip_type(ip_addr: str) -> IPType:
    """Get the type of ip address."""
    if ':' in ip_addr:
        return IPType.IPV6
    return IPType.IPV4

def complete_ip_str(abbreviation : str) -> str:
    """Complete the ip string from its abbreviations."""
    ip_addr = abbreviation.split('/')[0]
    if ':' in ip_addr:
        # The IP version is IPv6
        return ''.join(
            [
                str(ipaddress.IPv6Address(ip_addr).exploded),
                '/',
                ''.join(abbreviation.split('/')[1:]),
            ]
        ).rstrip("/")
    else:
        # The IP version is IPv4
        return ''.join(
            [
                str(ipaddress.IPv4Address(ip_addr).exploded),
                '/',
                ''.join(abbreviation.split('/')[1:]),
            ]
        ).rstrip("/")

def get_ip_segments(ip_addr: str) -> list[int]:
    """
    Take the string expression of IP address as input
    (Can be either IPv4 or IPv6, can be abbreviation of IP address),
    return the segments in int list.
    """
    ip_type : IPType = get_ip_type(ip_addr)
    full_ip_addr = complete_ip_str(ip_addr.split('/')[0])
    if ip_type == IPType.IPV6:
        ret_value = list(map(int, full_ip_addr.split(':')))
        if len(ret_value) != 8:
            raise ValueError(f"The IPv6 address should have 8 segments, while your address {full_ip_addr} has {len(ret_value)} segments")
        return ret_value
    else:
        ret_value = list(map(int, full_ip_addr.split('.')))
        if len(ret_value) != 4:
            raise ValueError(f"The IPv4 address should have 4 segments, while your address {full_ip_addr} has {len(ret_value)} segments")
        return ret_value

def is_valid_ipv4(ip_str: str):
    """
    Check if the tring is a valid IPv4 address.
    Return `True` if the address is a valid IPv4 address.
    Return `False` otherwise
    """
    parts = ip_str.split('.')
    # Must have 4 parts
    if len(parts) != 4:
        return False
    for part in parts:
        # Each part must be an integer
        if not part.isdigit():
            return False
        num = int(part)
        # Each number must be in 0-255
        if num < 0 or num > 255:
            return False
        # Check leading 0's
        if len(part) > 1 and part[0] == '0':
            return False
    return True

def is_valid_ipv4_prefix(ip_str: str):
    """
    Check if the input string is a valid IPv4 prefix.
    """
    if '/' not in ip_str:
        return False

    ip_part, prefix_length = ip_str.split('/', 1)

    # Check if the prefix length is an integer in [0,32].
    if not prefix_length.isdigit():
        return False
    prefix_int = int(prefix_length)
    if prefix_int < 0 or prefix_int > 32:
        return False

    # Check the IP address part. 
    octets = ip_part.split('.')
    if len(octets) != 4:
        return False

    for octet in octets:
        if not octet.isdigit():
            return False
        num = int(octet)
        if num < 0 or num > 255:
            return False

    return True