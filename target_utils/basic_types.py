import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataclasses import dataclass
from bgp_utils.basic_types import IP, IPPrefix
from enum import Enum

class SoftwareType(Enum):
    """
    The type of routing software
    """
    UNDEFINED = -1
    FRR = 1

@dataclass
class Neighbor:
    """
    The dataclass defining the properties of a BGP neighbor
    """
    peer_ip : IP
    asn : int

class BGPConfiguration:
    """
    This class is used to configure the BGP instance.
    We want this to be transparent to software type.
    """
    def __init__(self,
                 asn : int = 65001,
                 router_id : IP = IP('1.1.1.1'),
                 local_prefixes : list[IPPrefix] = [],
                 neighbors : list[Neighbor] = []
                 ):
        """
        Initialize the BGP configuration
        """
        self.asn = asn
        self.router_id = router_id
        self.local_prefixes = local_prefixes
        self.neighbors = neighbors

    def append_local_prefix(self, prefix: IPPrefix):
        """
        Append a local prefix for the BGP instance.
        """
        if prefix not in self.local_prefixes:
            self.local_prefixes.append(prefix)
        else:
            print(f"Prefix {prefix} already in the configuration.")

    def remove_local_prefix(self, prefix: IPPrefix):
        """
        Remove a local prefix from the BGP instance.
        """
        if prefix in self.local_prefixes:
            self.local_prefixes.remove(prefix)
        else:
            print(f"Prefix {prefix} not in the configuration.")

    def append_neighbor(self, neighbor: Neighbor):
        """
        Append a neighbor for the BGP instance.
        """
        if neighbor not in self.neighbors:
            self.neighbors.append(neighbor)
        else:
            print(f"BGP neighbor {neighbor} already in the configuration.")

    def remove_neighbor(self, neighbor: Neighbor):
        """
        Remove a neighbor from the BGP instance.
        """
        if neighbor in self.neighbors:
            self.neighbors.remove(neighbor)
        else:
            print(f"BGP neighbor {neighbor} not in the configuration.")
