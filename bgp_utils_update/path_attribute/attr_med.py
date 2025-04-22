from ..basic_bfn_types import Number_BFN
from .attr_base import AttrType_BFN, AttrLength_BFN, BaseAttr_BFN, PathAttributeType
import numpy as np

class MED_BFN(Number_BFN):
    """
    Value of BGP MULTI_EXIT_DISC (MED) attribute.
    """
    def __init__(self,
                 med: int):
        """Initialize the MED BFN."""

        ###### Basic attributes ######

        super().__init__(num_val=med, num_len=4)

        ###### Set the weights ######
        self.weights = np.ones(len(MED_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        # No special attributes
        # Defined in `Number_BFN`
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "MED_BFN"
    
    ########## Get binary info ##########

    # Defined in `Number_BFN`

    ########## Update according to dependencies ##########
    
    # Defined in `Number_BFN`

    ########## Methods for generating random mutation ##########

    def random_med(self) -> int:
        """
        Return a random MED value.
        Just an encapsulation of the father class' method. 
        """
        return self.random_num()

    ########## Methods for applying mutation ##########

    def set_med(self, med: int):
        """
        Set the MED value of current BFN.
        Just an encapsulation of the father class' method. 
        So there is NO decorator. 
        """
        self.set_num(med)

    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = Number_BFN.mutation_set

class MEDAttr_BFN(BaseAttr_BFN):
    """
    BGP path attribute MULTI_EXIT_DISC.
    """
    def __init__(self, 
                 attr_value_bfn: MED_BFN):
        """Initialize the BGP MULTI_EXIT_DISC path attribute."""

        ###### Basic attributes ######

        super().__init__(attr_type_bfn=AttrType_BFN(PathAttributeType.MULTI_EXIT_DISC),
                         attr_len_bfn=AttrLength_BFN(length_val=4),
                         attr_value_bfn=attr_value_bfn)

        ###### Set the weights ######
        self.weights = np.ones(len(MEDAttr_BFN.mutation_set))
        self.weights /= np.sum(self.weights)
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "MEDAttr_BFN"

    ########## Get binary info ##########

    # Use methods from father class
    
    ########## Update according to dependencies ##########
    
    # Use methods from father class

    ########## Methods for generating random mutation ##########

    # Use methods from father class

    ########## Methods for applying mutation ##########

    # The following methods are recursively calling set-function of childrens, 
    # so there is no need to use `set_function_decorator`

    def set_med(self, med: int):
        """Set the med value of the MULTI_EXIT_DISC attribute."""
        bfn: MED_BFN = self.children[self.attr_value_key]
        bfn.set_med(med)
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BaseAttr_BFN.mutation_set
