from binary_utils.utils import * 
from .attr_base import PathAttributeType, BaseAttr
from enum import Enum

class OriginType(Enum):
    """
    The ORIGIN attribute type
    """
    IGP = 0
    EGP = 1
    INCOMPLETE = 2

class OriginAttr(BaseAttr):
    """
    BGP path attribute: ORIGIN
    """
    def __init__(self, orig_type=OriginType.EGP):
        """
        Initialization
        """
        ###### Initializing the content part ######
        self.origin_type: OriginType = orig_type
        ###### Initializing the binary part ######
        super().__init__()
        ###### Set the binary part ######
        self.reset()
    
    def reset(self):
        """
        Reset the attribute into the original status.
        """
        self.attr_flag_b : bytes = self.set_attr_flag(attribute=self.get_type(), ext_len=1)
        self.attr_type_b : bytes = self.set_attr_type(attribute=self.get_type())
        self.attr_len_b : bytes = num2bytes(1,1)
        self.attr_value_b : bytes = num2bytes(self.origin_type.value,1)

    def set_attr_value(self, **kwargs):
        """
        You can modify the `attr_value_b` of the attribute here.
        An alternative way of modifying the attribute value:
        1. origin_type: OriginType
        """
        if 'self_defined' in kwargs:
            self_defined = kwargs['self_defined']
            assert isinstance(self_defined, bytes)
            super().set_attr_value(self_defined)
            return
        elif 'origin_type' in kwargs:
            origin_type: OriginType = kwargs['origin_type']
            self.attr_value_b = num2bytes(origin_type.value, 1)
        else:
            raise ValueError("Invalid input parameter!")

    def get_type(self):
        return PathAttributeType.ORIGIN

    def set_origin_type(self, orig_type:OriginType):
        """
        Set the ORIGIN type of this attribute.
        """
        self.origin_type = orig_type
    