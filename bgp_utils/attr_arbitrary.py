from .attr_base import BaseAttr

class ArbitraryAttr(BaseAttr):
    """
    Arbitrary BGP path attribute.
    """
    def __init__(self,
                 attr_flag_b : bytes,
                 attr_type_b : bytes,
                 attr_len_b : bytes,
                 attr_value_b : bytes):
        """
        Initialize the arbitrary attribute.
        """
        self.attr_flag_b : bytes = attr_flag_b
        self.attr_type_b : bytes = attr_type_b
        self.attr_len_b : bytes = attr_len_b
        self.attr_value_b : bytes = attr_value_b
