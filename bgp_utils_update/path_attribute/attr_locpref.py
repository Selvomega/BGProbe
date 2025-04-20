from ..basic_types import Number_BFN
from .attr_base import AttrType_BFN, AttrLength_BFN, BaseAttr_BFN, PathAttributeType
import numpy as np

class LOCPREF_BFN(Number_BFN):
    """
    Value of BGP LOCAL_PREF (MED) attribute.
    """
    def __init__(self,
                 local_pref: int):
        """Initialize the LOCAL_PREF BFN."""

        ###### Basic attributes ######

        super().__init__(num_val=local_pref, num_len=4)

        ###### Set the weights ######
        self.weights = np.ones(len(LOCPREF_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        # No special attributes
        # Defined in `Number_BFN`
    
    @classmethod
    def get_bfn_name() -> str:
        """Get the name of the BFN."""
        return "LOCPREF_BFN"
    
    ########## Get binary info ##########

    # Defined in `Number_BFN`

    ########## Update according to dependencies ##########
    
    # Defined in `Number_BFN`

    ########## Methods for generating random mutation ##########

    def random_local_pref(self) -> int:
        """
        Return a random LOCAL_PREF value.
        Just an encapsulation of the father class' method. 
        """
        return self.random_num()

    ########## Methods for applying mutation ##########

    def set_local_pref(self, local_pref: int):
        """
        Set the LOCAL_PREF value of current BFN.
        Just an encapsulation of the father class' method. 
        So there is NO decorator. 
        """
        self.set_num(local_pref)

    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = Number_BFN.mutation_set

class LOCPREFAttr_BFN(BaseAttr_BFN):
    """
    BGP path attribute LOCAL_PREF.
    """
    def __init__(self, 
                 attr_value_bfn: LOCPREF_BFN):
        """Initialize the BGP LOCAL_PREF path attribute."""

        ###### Basic attributes ######

        super().__init__(attr_type_bfn=AttrType_BFN(PathAttributeType.LOCAL_PREF),
                         attr_len_bfn=AttrLength_BFN(length_val=4),
                         attr_value_bfn=attr_value_bfn)

        ###### Set the weights ######
        self.weights = np.ones(len(LOCPREFAttr_BFN.mutation_set))
        self.weights /= np.sum(self.weights)
    
    @classmethod
    def get_bfn_name() -> str:
        """Get the name of the BFN."""
        return "LOCPREFAttr_BFN"

    ########## Get binary info ##########

    # Use methods from father class
    
    ########## Update according to dependencies ##########
    
    # Use methods from father class

    ########## Methods for generating random mutation ##########

    # Use methods from father class

    ########## Methods for applying mutation ##########

    # The following methods are recursively calling set-function of childrens, 
    # so there is no need to use `set_function_decorator`

    def set_local_pref(self, local_pref: int):
        """Set the value of the LOCAL_PREF attribute."""
        bfn: LOCPREF_BFN = self.children[self.attr_value_key]
        bfn.set_local_pref(local_pref)

    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BaseAttr_BFN.mutation_set
