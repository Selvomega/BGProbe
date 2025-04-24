from ..binary_field_node import BinaryFieldNode
from ..basic_bfn_types import Length_BFN, ASN_BFN, BinaryFieldList_BFN
from .attr_base import AttrType_BFN, AttrLength_BFN, AttrValue_BFN, BaseAttr_BFN, PathAttributeType
from basic_utils.binary_utils import num2bytes, bytes2num
from enum import Enum
import random
import numpy as np

class PathSegementType(Enum):
    """
    Path segment type.
    """
    AS_SET = 1
    AS_SEQUENCE = 2

class PathSegementType_BFN(BinaryFieldNode):
    """
    Path segment type BFN.
    """
    def __init__(self, 
                 path_segment_type: PathSegementType):
        """Initialize the path segment type BFN."""

        ###### Basic attributes ######

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(PathSegementType_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        self.path_segment_type : PathSegementType_BFN = path_segment_type
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "PathSegementType_BFN"

    ########## Get binary info ##########

    def get_binary_expression_inner(self):
        """Get binary expression."""
        # Concatenate the children's binary expressions.
        return num2bytes(self.path_segment_type.value,1)

    ########## Update according to dependencies ##########
    
    def update_on_dependencies_inner(self):
        """
        Update the current BFN according to its dependencies.
        This BFN do not have dependencies.
        """
        # You should not raise error because of `attach` function
        return
    
    ########## Methods for generating random mutation ##########
    
    def random_path_segment_type(self) -> PathSegementType:
        """
        Return a random path segment type.
        """
        valid_path_segment_types = [
            member for member in PathSegementType
        ]
        return random.choice(valid_path_segment_types)
    
    ########## Methods for applying mutation ##########

    @BinaryFieldNode.set_function_decorator
    def set_path_segment_type(self,path_segment_type: PathSegementType):
        """
        Set the ORIGIN attribute type.
        """
        self.path_segment_type = path_segment_type
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set + [
        BinaryFieldNode.MutationItem(random_path_segment_type,set_path_segment_type)
    ]

class PathSegmentLength_BFN(Length_BFN):
    """
    BGP path segment length BFN.
    Inherit the `Length_BFN` field.
    """

    def __init__(self,
                 length_val: int):
        """
        Initialize the path segment length BFN
        """

        ###### Basic attributes ######

        super().__init__(length_val=length_val,
                         length_byte_len=1,
                         include_myself=False)

        ###### Set the weights ######
        self.weights = np.ones(len(PathSegmentLength_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "PathSegmentLength_BFN"
    
    ######### Update according to dependencies ##########
    
    def update_on_dependencies_inner(self):
        """
        Update the current BFN according to its dependencies.
        """
        self.include_myself = False
        as_num = 0
        for dependency in self.dependencies.values():
            as_num = as_num + dependency.get_list_len()
        self.num_val = as_num

class ASNList_BFN(BinaryFieldList_BFN):
    """
    BGP AS number list.
    When inheriting `BinaryFieldList_BFN`, only need to rewrite the `__init__` method
    """
    def __init__(self, 
                 bfn_list : list[ASN_BFN]):
        """Initialize by calling BinaryFieldList_BFN's `__init__` method."""
        super().__init__(bfn_list, ASN_BFN.get_bfn_name())

PathSegmentValue_BFN = ASNList_BFN

class PathSegment_BFN(BinaryFieldNode):
    """
    BGP Path Segment path attribute BFN.
    """
    
    def __init__(self,
                 pathseg_type_bfn: PathSegementType_BFN,
                 pathseg_len_bfn: PathSegmentLength_BFN,
                 pathseg_val_bfn: PathSegmentValue_BFN):
        """
        Initialize the BGP Path Segment attribute BFN.
        """

        ###### Basic attributes ######

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(PathSegment_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        # No special attributes

        ###### Deal with relations with and between children ######

        # Initialize the children. 
        # The sequence is very important.
        # Parents can still be `None`
        self.pathseg_type_key = self.append_child(pathseg_type_bfn)
        self.pathseg_len_key  = self.append_child(pathseg_len_bfn)
        self.pathseg_val_key = self.append_child(pathseg_val_bfn)
        # Update the detach state of the current BFN.
        self.detach_according_to_children()
        # Add dependencies between children
        self.add_dependency_between_children(dependent_key=self.pathseg_len_key,
                                             dependency_key=self.pathseg_val_key)
        # Let children update
        self.children_update()
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "PathSegment_BFN"

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

    def set_path_segment_type(self, pathseg_type: PathSegementType):
        """Set the type of the path segment."""
        bfn: PathSegementType_BFN = self.children[self.pathseg_type_key]
        bfn.set_path_segment_type(pathseg_type)
    
    def set_path_segment_length(self, pathseg_len: int):
        """Set the length of the path segment."""
        bfn: PathSegmentLength_BFN = self.children[self.pathseg_len_key]
        bfn.set_length(pathseg_len)
    
    def set_path_segment_value(self, asn_list: list[int]):
        """Set the value of path segment."""
        bfn: PathSegmentValue_BFN = self.children[self.pathseg_val_key]
        bfn.set_bfn_list([ASN_BFN(asn) for asn in asn_list])
    
    def append_as_to_path_segment(self, asn: int):
        """Append an AS number to the path segment value."""
        bfn: PathSegmentValue_BFN = self.children[self.pathseg_val_key]
        bfn.append_bfn(ASN_BFN(asn))

    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set

class ASPath_BFN(BinaryFieldList_BFN):
    """
    Value of BGP AS_PATH path attribute. 
    """
    def __init__(self,
                 pathseg_list: list[PathSegment_BFN]):
        """Initialize the Origin attribute type BFN."""

        ###### Basic attributes ######

        super().__init__(bfn_list=pathseg_list,
                         list_element_name=PathSegment_BFN.get_bfn_name())

        ###### Set the weights ######
        self.weights = np.ones(len(ASPath_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

class ASPathAttr_BFN(BaseAttr_BFN):
    """
    BGP path attribute AS_PATH.
    """
    def __init__(self, 
                 attr_value_bfn: ASPath_BFN, 
                 attr_len_bfn: AttrLength_BFN = None):
        """Initialize the BGP AS_PATH path attribute"""

        ###### Redefine default input parameters to avoid shallow-copy ######

        if attr_len_bfn is None:
            attr_len_bfn = AttrLength_BFN(length_val=0)

        ###### Basic attributes ######

        super().__init__(attr_type_bfn=AttrType_BFN(PathAttributeType.AS_PATH),
                         attr_len_bfn=attr_len_bfn,
                         attr_value_bfn=attr_value_bfn)

        ###### Set the weights ######
        self.weights = np.ones(len(ASPathAttr_BFN.mutation_set))
        self.weights /= np.sum(self.weights)
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "ASPathAttr_BFN"

    ########## Get binary info ##########

    # Use methods from father class
    
    ########## Update according to dependencies ##########
    
    # Use methods from father class

    ########## Methods for generating random mutation ##########

    # Use methods from father class

    ########## Methods for applying mutation ##########

    # The following methods are recursively calling set-function of childrens, 
    # so there is no need to use `set_function_decorator`

    def append_aspath_segment(self, aspath_seg: PathSegementType_BFN):
        """Append a path segment to the AS_PATH attribute."""
        bfn: ASPath_BFN = self.children[self.attr_value_bfn]
        bfn.append_bfn(aspath_seg)
    
    def set_aspath_list(self, aspath_seg_list: list[PathSegementType_BFN]):
        """Set the list of the Path Segments."""
        bfn: ASPath_BFN = self.children[self.attr_value_bfn]
        bfn.set_bfn_list(aspath_seg_list)

    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BaseAttr_BFN.mutation_set
