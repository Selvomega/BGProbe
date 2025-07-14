import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dataclasses import dataclass
from enum import Enum

class RouterAgentType(Enum):
    """
    The type of routing software
    """
    UNDEFINED = -1
    FRR = 1
    BIRD = 2
    GOBGP = 3

@dataclass
class Neighbor:
    """
    The dataclass defining the properties of a BGP neighbor
    """
    peer_ip : str
    peer_asn : int
    # local source used for communication
    local_source : str

class RouterAgentConfiguration:
    """
    This class is used to configure the BGP instance.
    We want this to be transparent to software type.
    """
    def __init__(self,
                 asn : int = 65001,
                 router_id : str = '1.1.1.1',
                 local_prefixes : list[str] = [],
                 neighbors : list[Neighbor] = [],
                 router_type: RouterAgentType = RouterAgentType.FRR
                 ):
        """
        Initialize the BGP configuration
        """
        self.asn : int = asn
        self.router_id : str = router_id
        self.local_prefixes : list[str] = local_prefixes
        self.neighbors : list[Neighbor] = neighbors
        self.router_type : RouterAgentType = router_type

    def get_router_type(self) -> RouterAgentType:
        """Get the router software type."""
        return self.router_type
    
    def get_string_expression(self) -> str:
        """
        Get the string expression of the router agent configuration.
        """
        return f"""ASN: {self.asn}
router id: {self.router_id}
local prefixes: {self.local_prefixes}
neighbors: {self.neighbors}
router type: {self.router_type.name}"""


    ########## Deprecated ##########

    # def append_local_prefix(self, prefix: str):
    #     """
    #     Append a local prefix for the BGP instance.
    #     return True if you can make some modification
    #     return False if no modification should be made
    #     """
    #     modify  = prefix not in self.local_prefixes
    #     if modify:
    #         self.local_prefixes.append(prefix)
    #     else:
    #         print(f"Prefix {prefix} already in the configuration.")
    #     return modify

    # def remove_local_prefix(self, prefix: str):
    #     """
    #     Remove a local prefix from the BGP instance.
    #     return True if you can make some modification
    #     return False if no modification should be made
    #     """
    #     modify = prefix in self.local_prefixes
    #     if modify:
    #         self.local_prefixes.remove(prefix)
    #     else:
    #         print(f"Prefix {prefix} not in the configuration.")
    #     return modify

    # def append_neighbor(self, neighbor: Neighbor):
    #     """
    #     Append a neighbor for the BGP instance.
    #     return True if you can make some modification
    #     return False if no modification should be made
    #     """
    #     modify = neighbor not in self.neighbors
    #     if modify:
    #         self.neighbors.append(neighbor)
    #     else:
    #         print(f"BGP neighbor {neighbor} already in the configuration.")
    #     return modify

    # def remove_neighbor(self, neighbor: Neighbor):
    #     """
    #     Remove a neighbor from the BGP instance.
    #     return True if you can make some modification
    #     return False if no modification should be made
    #     """
    #     modify = neighbor in self.neighbors
    #     if modify:
    #         self.neighbors.remove(neighbor)
    #     else:
    #         print(f"BGP neighbor {neighbor} not in the configuration.")
    #     return neighbor in self.neighbors
