from .attr_base import AttrType_BFN, AttrLength_BFN, BaseAttr_BFN, PathAttributeType
from ..basic_types import IPv4Address_BFN
import numpy as np

NextHop_BFN = IPv4Address_BFN

class NextHopAttr_BFN(BaseAttr_BFN):
    """
    BGP path attribute NEXT_HOP.
    """
    def __init__(self, 
                 attr_value_bfn: NextHop_BFN):
        """Initialize the BGP NEXT_HOP path attribute."""

        ###### Basic attributes ######

        super().__init__(attr_type_bfn=AttrType_BFN(PathAttributeType.NEXT_HOP),
                         attr_len_bfn=AttrLength_BFN(length_val=4),
                         attr_value_bfn=attr_value_bfn)

        ###### Set the weights ######
        self.weights = np.ones(len(NextHopAttr_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

    @classmethod
    def get_bfn_name() -> str:
        """Get the name of the BFN."""
        return "NextHopAttr_BFN"

    ########## Get binary info ##########

    # Use methods from father class
    
    ########## Update according to dependencies ##########
    
    # Use methods from father class

    ########## Methods for generating random mutation ##########

    # Use methods from father class

    ########## Methods for applying mutation ##########

    # The following methods are recursively calling set-function of childrens, 
    # so there is no need to use `set_function_decorator`

    def set_next_hop(self, ip_addr: str):
        """Set the next hop address of the NEXT_HOP attribute."""
        bfn: NextHop_BFN = self.children[self.attr_value_key]
        bfn.set_ip_addr(ip_addr)
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BaseAttr_BFN.mutation_set
