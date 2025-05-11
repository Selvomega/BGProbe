from ..binary_field_node import BinaryFieldNode
from ..basic_bfn_types import Length_BFN
from basic_utils.binary_utils import num2bytes, bytes2num, list2byte
from enum import Enum
import random
import numpy as np

class PathAttributeType(Enum):
    """
    BGP path attribute code
    """
    RESERVED = 0
    ORIGIN = 1
    AS_PATH = 2
    NEXT_HOP = 3
    MULTI_EXIT_DISC = 4
    LOCAL_PREF = 5
    ATOMIC_AGGREGATE = 6
    AGGREGATOR = 7
    COMMUNITIES = 8
    ORIGINATOR_ID = 9
    CLUSTER_LIST = 10
    MP_REACH_NLRI = 14
    MP_UNREACH_NLRI = 15

def calculate_attr_type_property(attr_type: PathAttributeType):
    """
    Calculate the property of the attribute type.
    Return values: 
    1. If the path attribute type is optional.
    2. If the path attribute type is transitive.
    --------------------
    Well-known attributes must be transitive.
    Mandatory attributes MUST be included in every UPDATE message that contains NLRI.
    """
    match attr_type:
        case PathAttributeType.RESERVED:
            # If the type is `PathAttributeType.RESERVED`, return a default value
            return True, True
            raise ValueError(f"Invalid path attribute: {PathAttributeType.RESERVED}")
        case PathAttributeType.ORIGIN | PathAttributeType.AS_PATH | PathAttributeType.NEXT_HOP | PathAttributeType.LOCAL_PREF | PathAttributeType.ATOMIC_AGGREGATE:
            return False, True
        case PathAttributeType.AGGREGATOR | PathAttributeType.COMMUNITIES:
            return True, True
        case PathAttributeType.MULTI_EXIT_DISC | PathAttributeType.ORIGINATOR_ID | PathAttributeType.CLUSTER_LIST:
            return True, False
        case PathAttributeType.MP_REACH_NLRI | PathAttributeType.MP_UNREACH_NLRI:
            return True, False
        case _:
            raise ValueError(f"Path attribute {attr_type} undefined!")

# Attribute Type is a two-octet field that consists of the Attribute Flags octet, 
# followed by the Attribute Type Code octet.
# 0               1
# 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |  Attr. Flags  |Attr. Type Code|
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

class AttrType_BFN(BinaryFieldNode):
    """
    BGP path attribute type.
    """
    def __init__(self,
                 attr_type: PathAttributeType = PathAttributeType.RESERVED,
                 is_partial: bool = False,
                 ext_len: bool = False):
        """Initialize the attribute type BFN."""
        
        ###### Basic attributes ######

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(AttrType_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        is_optional, is_transitive = calculate_attr_type_property(attr_type)

        self.is_optional : bool = is_optional
        self.is_transitive : bool = is_transitive
        self.is_partial : bool = is_partial
        self.ext_len : bool = ext_len
        # The remaining for bits of the AttrType Octet.
        self.lower_bits : list[int] = [0,0,0,0]
        self.attr_type_code : int = attr_type.value
        # This attribute is unused. 
        self.attr_type : PathAttributeType = attr_type

    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "AttrType_BFN"

    ########## Factory methods: Create an instance of the class ##########

    @classmethod
    def get_bfn(cls,
                type_code: int,
                higher_bits: list[int],
                lower_bits: list[int] = None) -> "AttrType_BFN":
        """
        Get the DIY attribute type BFN.
        """
        # Initialize the defaut parameters
        if lower_bits is None:
            lower_bits = [0,0,0,0]
        # First check the format of the input 
        if len(higher_bits)!=4 or len(lower_bits)!=4:
            raise ValueError("The length of `higher_bits` and `lower_bits` must be 4!")
        if any(bit not in (0, 1) for bit in higher_bits) or any(bit not in (0, 1) for bit in lower_bits):
            raise ValueError("The list element of `higher_bits` and `lower_bits` must be 0 or 1!")
        # First initialize a random one and then modify.
        ret : AttrType_BFN = AttrType_BFN()
        ret.is_optional = higher_bits[0]==1
        ret.is_transitive = higher_bits[1]==1
        ret.is_partial = higher_bits[2]==1
        ret.ext_len = higher_bits[3]==1
        ret.lower_bits = lower_bits
        ret.attr_type_code = type_code
        # Return 
        return ret

    ########## Get binary info ##########

    def get_binary_expression_inner(self):
        """Get binary expression."""
        bit_list = [
            1 if self.is_optional else 0,
            1 if self.is_transitive else 0,
            1 if self.is_partial else 0,
            1 if self.ext_len else 0,
        ] + self.lower_bits
        return list2byte(bit_list) + num2bytes(self.attr_type_code,1)

    ########## Update according to dependencies ##########
    
    def update_on_dependencies_inner(self):
        """
        Update the current BFN according to its dependencies.
        This BFN do not have dependencies.
        """
        # You should not raise error because of `attach` function
        return

    ########## Methods for generating random mutation ##########

    def random_lower_bits(self) -> int:
        """
        Return a random list of lower bits of this field.
        """
        bit_list = [random.randint(0,1) for _ in range(0,4)]
        return bit_list
    
    def random_attr_type(self) -> PathAttributeType:
        """
        Return a random path attribute type.
        """
        valid_attr_types = [
            member for member in PathAttributeType if member != PathAttributeType.RESERVED
        ]
        return random.choice(valid_attr_types)
    
    def random_attr_type_code(self) -> int:
        """
        Return a random path attribute type code.
        """
        byte_seq = random.randbytes(1)
        return bytes2num(byte_seq)

    ########## Methods for applying mutation ##########

    @BinaryFieldNode.set_function_decorator
    def set_is_optional(self,is_optional: bool):
        """Set if the path attribute is optional or not."""
        self.is_optional = is_optional

    @BinaryFieldNode.set_function_decorator
    def set_is_transitive(self,is_transitive: bool):
        """Set if the path attribute is transitive or not."""
        self.is_transitive = is_transitive

    @BinaryFieldNode.set_function_decorator
    def set_is_partial(self,is_partial: bool):
        """Set if the path attribute is partial or not."""
        self.is_partial = is_partial

    @BinaryFieldNode.set_function_decorator
    def set_ext_len(self,ext_len: bool):
        """Set if the path attribute uses extended length field or not."""
        self.ext_len = ext_len

    @BinaryFieldNode.set_function_decorator
    def set_lower_bits(self,lower_bits: list[int]):
        """Set the lower 4 bits of the attribute type flag field."""
        if len(lower_bits) != 4:
            raise ValueError("The input bit list must have length 4!")
        if any(bit not in (0, 1) for bit in lower_bits):
            raise ValueError("The list element must be 0 or 1!")
        self.lower_bits = lower_bits

    @BinaryFieldNode.set_function_decorator
    def set_attr_type(self, attr_type: PathAttributeType):
        """Set the path attribute type."""
        is_optional, is_transitive = calculate_attr_type_property(attr_type)
        self.is_optional : bool = is_optional
        self.is_transitive : bool = is_transitive
        self.attr_type_code : int = attr_type.value
        self.attr_type : PathAttributeType = attr_type

    @BinaryFieldNode.set_function_decorator
    def set_attr_type_code(self, attr_type_code: int):
        """Set the path attribute type code."""
        self.attr_type_code = attr_type_code

    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set + [
        BinaryFieldNode.MutationItem(random_lower_bits, set_lower_bits),
        BinaryFieldNode.MutationItem(random_attr_type, set_attr_type),
        BinaryFieldNode.MutationItem(random_attr_type_code, set_attr_type_code)
    ]

class AttrLength_BFN(Length_BFN):
    """
    BGP path attribute length BFN.
    Inherit the `Length_BFN` field.
    """

    def __init__(self, 
                 length_val: int, 
                 length_byte_len: int = 1):
        """Initialize the BGP path attribute length BFN."""

        ###### Basic attributes ######

        super().__init__(length_val=length_val,
                         length_byte_len=length_byte_len,
                         include_myself=False)

        ###### Set the weights ######
        self.weights = np.ones(len(AttrLength_BFN.mutation_set))
        self.weights /= np.sum(self.weights)
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "AttrLength_BFN"

    ######### Update according to dependencies ##########
    
    def update_on_dependencies_inner(self):
        """
        Update the current BFN according to its dependencies.
        """
        self.include_myself = False
        len_sum = 0
        for dependency_key, dependency_value in self.dependencies.items():
            if dependency_key.startswith(AttrType_BFN.get_bfn_name()):
                self.num_len = 2 if dependency_value.ext_len else 1
            else:
                len_sum = len_sum + dependency_value.get_binary_length()
        self.num_val = len_sum

AttrValue_BFN = BinaryFieldNode

class BaseAttr_BFN(BinaryFieldNode):
    """
    BGP Base Path Attribute.
    This can be inherited by more specific path attribute types. 
    """
    def __init__(self,
                 attr_type_bfn: AttrType_BFN,
                 attr_len_bfn: AttrLength_BFN,
                 attr_value_bfn: AttrValue_BFN):
        """Initialize the BGP path attribute."""

        ###### Basic attributes ######

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(BaseAttr_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        # No special attributes

        ###### Deal with relations with and between children ######

        # Initialize the children. 
        # The sequence is very important.
        # Parents can still be `None`
        self.attr_type_key = self.append_child(attr_type_bfn)
        self.attr_len_key = self.append_child(attr_len_bfn)
        self.attr_value_key = self.append_child(attr_value_bfn)
        # Update the detach state of the current BFN.
        self.detach_according_to_children()
        # Add dependencies between children
        # Defines the length field length.
        self.add_dependency_between_children(dependent_key=self.attr_len_key,
                                             dependency_key=self.attr_type_key)
        # Defines the length field value.
        self.add_dependency_between_children(dependent_key=self.attr_len_key,
                                             dependency_key=self.attr_value_key)
        # Let children update
        self.children_update()
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "BaseAttr_BFN"
    
    ########## Get binary info ##########

    def get_binary_expression_inner(self):
        """Get binary expression."""
        # Concatenate the children's binary expressions.
        return b''.join([
            child.get_binary_expression() for child in self.children.values()
        ])
    
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

    # The following methods are recursively calling set-function of childrens, 
    # so there is no need to use `set_function_decorator`

    def set_length(self, length_val: int):
        """
        Set the length of the Attribute BFN.
        """
        bfn : AttrLength_BFN = self.children[self.attr_len_key]
        bfn.set_length(length_val)

    def set_message_type(self, attr_type: PathAttributeType):
        """
        Set the attribute type of the Attribute BFN.
        """
        bfn: AttrType_BFN = self.children[self.attr_type_key]
        bfn.set_attr_type(attr_type)
    
    def set_attr_val_bval(self, attr_val: bytes):
        """
        Set the attribute value of the Attribute BFN.
        """
        bfn : AttrValue_BFN = self.children[self.attr_value_key]
        bfn.set_bval(attr_val)
    
    def set_attr_type_lower_bits(self,lower_bits: list[int]):
        """Set the lower 4 bits of the attribute type flag field."""
        bfn: AttrType_BFN = self.children[self.attr_type_key]
        bfn.set_lower_bits(lower_bits)

    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set
