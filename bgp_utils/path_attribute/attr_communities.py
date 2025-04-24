from ..basic_bfn_types import BinaryFieldNode
from .attr_base import AttrType_BFN, AttrLength_BFN, AttrValue_BFN, BaseAttr_BFN, PathAttributeType
from basic_utils.binary_utils import num2bytes, bytes2num
from enum import Enum
from functools import partial
import random
import numpy as np

def compose_communities_value(asn:int,operation:int) -> bytes:
    """
    Compose the communities attribute value.
    """
    return num2bytes(asn,4) + num2bytes(operation,4)

def decompose_communities_value(communities_val: bytes) -> tuple[int,int]:
    """
    Decompose the communities attribute value.
    """
    if len(communities_val)!=4:
        raise ValueError("The input communities length must be 4 bytes.")
    return bytes2num(communities_val[:2]), bytes2num(communities_val[2:])

class WellKnownCommunities(Enum):
    """
    Well-known Communities.
    """
    NO_EXPORT = b'\xFF\xFF\xFF\x01'
    NO_ADVERTISE = b'\xFF\xFF\xFF\x02'
    NO_EXPORT_SUBCONFED = b'\xFF\xFF\xFF\x03'

class Communities_BFN(AttrValue_BFN):
    """
    Value of BGP COMMUNITIES (MED) attribute.
    """
    def __init__(self,
                 asn: int,
                 operation: int):
        """Iitialize the BGP COMMUNITIES value."""
        
        ###### Basic attributes ######

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(Communities_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        self.asn : int = asn
        self.operation : int = operation
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "Communities_BFN"

    ########## Get binary info ##########

    def get_binary_expression_inner(self):
        """Get binary expression."""
        # Concatenate the children's binary expressions.
        return compose_communities_value(self.asn, self.operation)

    ########## Update according to dependencies ##########
    
    def update_on_dependencies_inner(self):
        """
        Update the current BFN according to its dependencies.
        This BFN do not have dependencies.
        """
        # You should not raise error because of `attach` function
        return
    
    ########## Methods for generating random mutation ##########

    def random_asn(self) -> int:
        """
        Return a random ASN for the COMMUNITIES attribute.
        """
        byte_seq = random.randbytes(2)
        return bytes2num(byte_seq)
    
    def random_operation(self) -> int:
        """
        Return a random operation for the COMMUNITIES attribute.
        """
        byte_seq = random.randbytes(2)
        return bytes2num(byte_seq)
    
    def random_valid_communities(self) -> WellKnownCommunities:
        """
        Return a random ORIGIN attribute type.
        """
        valid_communities = [
            member for member in WellKnownCommunities
        ]
        return random.choice(valid_communities)
    
    ########## Methods for applying mutation ##########

    @BinaryFieldNode.set_function_decorator
    def set_asn(self, asn:int):
        """
        Set the ASN for the COMMUNITIES attribute.
        """
        self.asn = asn

    @BinaryFieldNode.set_function_decorator
    def set_operation(self, operation:int):
        """
        Set the operation for the COMMUNITIES attribute.
        """
        self.operation = operation

    @BinaryFieldNode.set_function_decorator
    def set_valid_communities(self,communities: WellKnownCommunities):
        """
        Set the COMMUNITIES attribute type.
        The input parameter is a valid COMMUNITIES value.
        """
        asn, operation = decompose_communities_value(communities.value)
        self.asn = asn
        self.operation = operation
    
    @BinaryFieldNode.set_function_decorator
    def set_communities(self,communities: bytes):
        """
        Set the COMMUNITIES attribute type.
        The input parameter is a random 4-byte sequence
        """
        asn, operation = decompose_communities_value(communities)
        self.asn = asn
        self.operation = operation
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set + [
        BinaryFieldNode.MutationItem(random_asn, set_asn),
        BinaryFieldNode.MutationItem(random_operation, set_operation),
        BinaryFieldNode.MutationItem(random_valid_communities, set_valid_communities),
        BinaryFieldNode.MutationItem(
            partial(BinaryFieldNode.random_bval_fixed_len, 
                    length=4), 
            set_communities
        )
    ]

class CommunitiesAttr_BFN(BaseAttr_BFN):
    """
    BGP path attribute COMMUNITIES.
    """    
    def __init__(self, 
                 attr_value_bfn: Communities_BFN):
        """Initialize the BGP COMMUNITIES path attribute."""

        ###### Basic attributes ######

        super().__init__(attr_type_bfn=AttrType_BFN(PathAttributeType.COMMUNITIES),
                         attr_len_bfn=AttrLength_BFN(length_val=4),
                         attr_value_bfn=attr_value_bfn)

        ###### Set the weights ######
        self.weights = np.ones(len(CommunitiesAttr_BFN.mutation_set))
        self.weights /= np.sum(self.weights)
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "CommunitiesAttr_BFN"

    ########## Get binary info ##########

    # Use methods from father class

    ########## Update according to dependencies ##########

    # Use methods from father class

    ########## Methods for generating random mutation ##########

    # Use methods from father class

    ########## Methods for applying mutation ##########

    # The following methods are recursively calling set-function of childrens, 
    # so there is no need to use `set_function_decorator`

    def set_communities(self,communities: bytes):
        """
        Set the COMMUNITIES attribute value.
        """
        bfn: Communities_BFN = self.children[self.attr_value_key]
        bfn.set_communities(communities)

    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BaseAttr_BFN.mutation_set
