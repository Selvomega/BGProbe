from ..basic_bfn_types import BinaryFieldNode
from .attr_base import AttrType_BFN, AttrLength_BFN, BaseAttr_BFN
import numpy as np

class Arbitrary_BFN(BinaryFieldNode):
    """
    Value of arbitrary BGP path attribute.
    """
    def __init__(self,
                 value: bytes):
        """Initialize the Arbitrary attribute value BFN."""

        ###### Basic attributes ######

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(Arbitrary_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        self.value = value

    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "Arbitrary_BFN"
    
    ########## Get binary info ##########

    def get_binary_expression_inner(self):
        """Get binary expression."""
        return self.value

    ########## Update according to dependencies ##########
    
    def update_on_dependencies_inner(self):
        """
        Update the current BFN according to its dependencies.
        This BFN do not have dependencies.
        """
        # You should not raise error because of `attach` function
        return
    
    ########## Methods for generating random mutation ##########
    
    # Use methods from father class

    ########## Methods for applying mutation ##########

    @BinaryFieldNode.set_function_decorator
    def set_value(self, value: bytes):
        """
        Set the value of the aribitrary attribute.
        """
        self.value = value
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set + [
        BinaryFieldNode.MutationItem(BinaryFieldNode.random_bval,set_value)
    ]

# TODO: implement the get_instance method of `AttrType_BFN`

class ArbitraryAttr_BFN(BaseAttr_BFN):
    """
    Arbitrary BGP path attribute.
    """
    def __init__(self,
                 attr_type_bfn: AttrType_BFN,
                 attr_value_bfn: Arbitrary_BFN):
        """Initialize the Arbitrary BGP path attribute."""

        ###### Basic attributes ######

        super().__init__(attr_type_bfn=attr_type_bfn,
                         attr_len_bfn=AttrLength_BFN(length_val=1),
                         attr_value_bfn=attr_value_bfn)

        ###### Set the weights ######
        self.weights = np.ones(len(ArbitraryAttr_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "ArbitraryAttr_BFN"
    
    ########## Get binary info ##########

    # Use methods from father class
    
    ########## Update according to dependencies ##########
    
    # Use methods from father class

    ########## Methods for generating random mutation ##########

    # Use methods from father class

    ########## Methods for applying mutation ##########

    # The following methods are recursively calling set-function of childrens, 
    # so there is no need to use `set_function_decorator`

    def set_value(self, value: bytes):
        """
        Set the value of the aribitrary attribute.
        """
        bfn : Arbitrary_BFN = self.children[self.attr_value_key]
        bfn.set_value(value)
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BaseAttr_BFN.mutation_set
