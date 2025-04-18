from ..binary_field_node import BinaryFieldNode
from enum import Enum

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

# TODO: function to calculate `PathAttributeType` property

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

class BaseAttr_BFN(BinaryFieldNode):
    """
    BGP Base Path Attribute.
    This can be inherited by more specific path attribute types. 
    """

