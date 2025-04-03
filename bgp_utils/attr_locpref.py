from attr_base import PathAttributeType, BaseAttr
from binary_utils import * 

class LocalPrefAttr(BaseAttr):
    """
    BGP path attribute: LOCAL_PREF
    """
    def __init__(self, local_pref: int):
        """
        Initialization
        """
        ###### Initializing the content part ######
        self.local_pref: int = local_pref
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
        # The length of LOCAL_PREF field is 4
        self.attr_len_b : bytes = num2bytes(4,1)
        self.attr_value_b : bytes = num2bytes(self.local_pref,4)

    def set_attr_value(self, **kwargs):
        """
        You can modify the `attr_value_b` of the attribute here.
        An alternative ways of modifying the attribute value:
        1. local_pref: int
        """
        if 'self_defined' in kwargs:
            self_defined = kwargs['self_defined']
            assert isinstance(self_defined, bytes)
            super().set_attr_value(self_defined)
            return
        elif 'local_pref' in kwargs:
            local_pref: int = kwargs['local_pref']
            self.attr_value_b = num2bytes(local_pref,4)
        else:
            raise ValueError("Invalid input parameter!")

    def get_type(self):
        return PathAttributeType.LOCAL_PREF
    
    def set_locpref(self, local_pref):
        """
        Set the LOCAL_PREF value.
        """
        self.local_pref = local_pref
