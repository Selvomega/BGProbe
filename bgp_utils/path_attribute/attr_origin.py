from ..binary_field_node import BinaryFieldNode
from .attr_base import AttrType_BFN, AttrLength_BFN, AttrValue_BFN, BaseAttr_BFN, PathAttributeType
from basic_utils.binary_utils import num2bytes, bytes2num
from enum import Enum
import random
import numpy as np

class OriginType(Enum):
    """
    The ORIGIN attribute type
    """
    IGP = 0
    EGP = 1
    INCOMPLETE = 2

class Origin_BFN(AttrValue_BFN):
    """
    Value of BGP ORIGIN path attribute. 
    """
    def __init__(self,
                 origin_type: OriginType):
        """Initialize the Origin attribute type BFN."""
        
        ###### Basic attributes ######

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(Origin_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        self.origin_type : OriginType = origin_type
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "Origin_BFN"
    
    ########## Get binary info ##########

    def get_binary_expression_inner(self):
        """Get binary expression."""
        # Concatenate the children's binary expressions.
        return num2bytes(self.origin_type.value,1)

    ########## Update according to dependencies ##########
    
    def update_on_dependencies_inner(self):
        """
        Update the current BFN according to its dependencies.
        This BFN do not have dependencies.
        """
        # You should not raise error because of `attach` function
        return

    ########## Methods for generating random mutation ##########
    
    def random_origin_type(self) -> OriginType:
        """
        Return a random ORIGIN attribute type.
        """
        valid_origin_types = [
            member for member in OriginType
        ]
        return random.choice(valid_origin_types)
    
    ########## Methods for applying mutation ##########

    @BinaryFieldNode.set_function_decorator
    def set_origin_type(self,origin_type: OriginType):
        """
        Set the ORIGIN attribute type.
        """
        self.origin_type = origin_type
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set + [
        BinaryFieldNode.MutationItem(random_origin_type,set_origin_type)
    ]

class OriginAttr_BFN(BaseAttr_BFN):
    """
    BGP path attribute ORIGIN.
    """
    def __init__(self, 
                 attr_value_bfn: Origin_BFN):
        """Initialize the BGP ORIGIN path attribute."""

        ###### Basic attributes ######

        super().__init__(attr_type_bfn=AttrType_BFN(PathAttributeType.ORIGIN),
                         attr_len_bfn=AttrLength_BFN(length_val=1),
                         attr_value_bfn=attr_value_bfn)

        ###### Set the weights ######
        self.weights = np.ones(len(OriginAttr_BFN.mutation_set))
        self.weights /= np.sum(self.weights)
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "OriginAttr_BFN"

    ########## Get binary info ##########

    # Use methods from father class
    
    ########## Update according to dependencies ##########
    
    # Use methods from father class

    ########## Methods for generating random mutation ##########

    # Use methods from father class

    ########## Methods for applying mutation ##########

    # The following methods are recursively calling set-function of childrens, 
    # so there is no need to use `set_function_decorator`

    def set_origin_type(self,origin_type: OriginType):
        """
        Set the ORIGIN attribute type.
        """
        bfn : Origin_BFN = self.children[self.attr_value_key]
        bfn.set_origin_type(origin_type)

    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BaseAttr_BFN.mutation_set
