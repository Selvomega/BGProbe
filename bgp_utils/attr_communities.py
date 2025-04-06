from binary_utils.utils import * 
from .attr_base import PathAttributeType, BaseAttr
from enum import Enum

# To Check: See if a community with invalid length (NOT 4 bytes) can be tolerated. 

def compute_communities_value(asn:int,operation:int) -> bytes:
    """
    Compute the communities attribute value.
    """
    return num2bytes(asn,4) + num2bytes(operation,4)

class WellKnownCommunities(Enum):
    """
    Well-known Communities.
    """
    NO_EXPORT = b'\xFF\xFF\xFF\x01'
    NO_ADVERTISE = b'\xFF\xFF\xFF\x02'
    NO_EXPORT_SUBCONFED = b'\xFF\xFF\xFF\x03'

class CommunitiesAttr(BaseAttr):
    """
    BGP path attribute: COMMUNITIES
    """
    def __init__(self, communities_list: list[bytes]):
        """
        Initialization
        """
        ###### Initializing the content part ######
        self.communities_list: list[bytes] = communities_list.copy()
        ###### Initializing the binary part ######
        super().__init__()
        ###### Set the binary part ######
        self.reset()

    def reset(self):
        """
        Reset the attribute into the original status.
        """
        attr_value_b = b''.join(self.communities_list)
        self.attr_flag_b : bytes = self.set_attr_flag(attribute=self.get_type(), ext_len=1)
        self.attr_type_b : bytes = self.set_attr_type(attribute=self.get_type())
        self.attr_len_b : bytes = num2bytes(len(attr_value_b),1)
        self.attr_value_b : bytes = attr_value_b

    def set_attr_value(self, **kwargs):
        """
        You can modify the `attr_value_b` of the attribute here.
        An alternative ways of modifying the attribute value:
        1. communities_list: list[bytes]
        """
        if 'self_defined' in kwargs:
            self_defined = kwargs['self_defined']
            assert isinstance(self_defined, bytes)
            super().set_attr_value(self_defined)
            return
        elif 'communities_list' in kwargs:
            communities_list: list[bytes] = kwargs['communities_list']
            self.attr_value_b = b''.join(communities_list)
        else:
            raise ValueError("Invalid input parameter!")

    def get_type(self):
        return PathAttributeType.COMMUNITIES

    def append_community(self,communities:bytes):
        """
        Append the communities to the end of the `communities_list`
        Check the length of the community to make sure that the community looks legal.
        """
        assert len(communities) == 4
        self.communities_list.append(communities)
