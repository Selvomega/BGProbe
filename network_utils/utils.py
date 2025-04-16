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
    if ip_type == IPType.IPV4:
        return list(map(int, full_ip_addr.split(':')))
    else:
        return list(map(int, full_ip_addr.split('.')))
