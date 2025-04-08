from data_utils.binary_utils import * 
from .attr_base import PathAttributeType, BaseAttr

class MultiExitDiscAttr(BaseAttr):
    """
    BGP path attribute: MULTI_EXIT_DISC
    """
    def __init__(self, med_value: int):
        """
        Initialization
        """
        ###### Initializing the content part ######
        self.med_value: int = med_value
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
        # The length of MED field is 4
        self.attr_len_b : bytes = num2bytes(4,1)
        self.attr_value_b : bytes = num2bytes(self.med_value,4)

    def set_attr_value(self, **kwargs):
        """
        You can modify the `attr_value_b` of the attribute here.
        An alternative ways of modifying the attribute value:
        1. med_value: int
        """
        if 'self_defined' in kwargs:
            self_defined = kwargs['self_defined']
            assert isinstance(self_defined, bytes)
            super().set_attr_value(self_defined)
            return
        elif 'med_value' in kwargs:
            med_value: int = kwargs['med_value']
            self.attr_value_b = num2bytes(med_value,4)
        else:
            raise ValueError("Invalid input parameter!")

    def get_type(self):
        return PathAttributeType.MULTI_EXIT_DISC
    
    def set_med(self, med_value):
        """
        Set the MED value.
        """
        self.med_value = med_value
