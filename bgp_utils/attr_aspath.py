from data_utils.binary_utils import * 
from .attr_base import PathAttributeType, BaseAttr
from .basic_types import *
from enum import Enum

class PathSegementType(Enum):
    """
    Path segment type.
    """
    AS_SET = 1
    AS_SEQUENCE = 2

class PathSegment:
    """
    Component of BGP AS_PATH attibute.
    """
    def __init__(self,
                 path_segment_type: PathSegementType,
                 as_list: ASPath):
        self.type = path_segment_type
        self.as_list = as_list
        # The path segment length is the number of ASes in the AS segment
        # (not the number of bytes)
        self.path_segment_length = len(self.as_list)

    def get_binary_expression(self):
        """
        Express the path segment in bytes
        """
        type_b = num2bytes(self.type.value,1)
        len_b = num2bytes(self.path_segment_length,1)
        # TODO how to express AS number into bytes (2-byte/4-byte)
        as_list_b = b''.join(num2bytes(asn,2) for asn in self.as_list)
        return type_b + len_b + as_list_b

PathSegmentList = list[PathSegment]

class ASPathAttr(BaseAttr):
    """
    BGP path attribute: AS_PATH
    """
    def __init__(self, path_segment_list:PathSegmentList):
        """
        Initialization
        """
        ###### Initializing the content part ######
        self.path_segment_list: PathSegmentList = path_segment_list
        ###### Initializing the binary part ######
        super().__init__()
        ###### Set the binary part ######
        self.reset()
    
    def reset(self):
        """
        Reset the attribute into the original status.
        """
        path_segments_b = b''.join(path_segment.get_binary_expression() for path_segment in self.path_segment_list)
        self.attr_flag_b : bytes = self.set_attr_flag(attribute=self.get_type(), ext_len=1)
        self.attr_type_b : bytes = self.set_attr_type(attribute=self.get_type())
        self.attr_len_b : bytes = num2bytes(len(path_segments_b),1)
        self.attr_value_b : bytes = path_segments_b

    def set_attr_value(self, **kwargs):
        """
        You can modify the `attr_value_b` of the attribute here.
        An alternative way of modifying the attribute value:
        origin_type: OriginType
        """
        if 'self_defined' in kwargs:
            self_defined = kwargs['self_defined']
            assert isinstance(self_defined, bytes)
            super().set_attr_value(self_defined)
            return
        else:
            raise ValueError("Invalid input parameter!")

    def get_type(self):
        return PathAttributeType.AS_PATH
