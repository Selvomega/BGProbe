"""
The optional parameter element of UPDATE message.
"""

from data_utils.binary_utils import *
from .basic_types import BinaryField
from enum import Enum

class OptionalType(Enum):
    """
    Optional parameter type.
    """
    UNDEFINED = -1
    CAPABILITY = 2

class ReadyToUseOptValue(Enum):
    """
    Some ready-to-use optional parameter values.
    """
    MP_BGP_IPV4 = b'\x01\x04\x00\x01\x00\x01'
    ROUTE_REFRESH = b'\x02\x00'
    ENHANCED_ROUTE_REFRESH = b'\x46\x00'
    GRACEFUL_RESTART = b'\x06\x00'

class OptionalParameterElem(BinaryField):
    """
    The unit of optional parameter
    """
    def __init__(self,
                 opt_type,
                 opt_value):
        """
        Initialize the optional parameters
        the `opt_type` can be of two types: `OptionalType` and `int`
        """
        opt_type_code = None
        opt_value_bytes = None
        if isinstance(opt_type, OptionalType):
            opt_type_code = opt_type.value
        elif isinstance(opt_type, int):
            opt_type_code = opt_type
        else:
            raise ValueError(f"Invalid type of parameter opt_type: {opt_type}.")
        if isinstance(opt_value, BinaryField):
            opt_value_bytes = opt_value.get_binary_expression()
        elif isinstance(opt_value, bytes):
            opt_value_bytes = opt_value
        else:
            raise ValueError(f"Invalid type or parameter opt_value: {opt_value}.")
        self.opt_type_b = num2bytes(opt_type_code, 1)
        self.opt_value_b = opt_value_bytes
        self.opt_value_len = len(self.opt_value_b)

    def set_opt_type(self, opt_type):
        """
        Set the type of the optional parameter element.
        """
        if isinstance(opt_type, OptionalType):
            self.opt_type_b = num2bytes(opt_type.value, 1)
        elif isinstance(opt_type, int):
            self.opt_type_b = num2bytes(opt_type, 1)
        elif isinstance(opt_type, bytes):
            self.opt_type_b = opt_type
        else:
            raise ValueError(f"Invalid parameter type opt_type: {opt_type}")

    def set_opt_value(self, opt_value):
        """
        Set the value of the optional parameter element.
        """
        if isinstance(opt_value, BinaryField):
            self.opt_type_b = opt_value.get_binary_expression()
        elif isinstance(opt_value, bytes):
            self.opt_type_b = opt_value
        else:
            raise ValueError(f"Invalid parameter type opt_value: {opt_value}")

    def set_opt_value_length(self, opt_value_length):
        """
        Set the length of the optional parameter element.
        """
        self.opt_value_len = opt_value_length

    def get_opt_type(self):
        """
        Get the type of the optional parameter element.
        """
        potential_type_code = bytes2num(self.opt_type_b)
        if potential_type_code in {item.value for item in OptionalType}:
            return OptionalType(potential_type_code)
        return OptionalType.UNDEFINED

    def get_opt_value_length(self) -> int:
        """
        Get the length of the value field. 
        """
        return self.opt_value_len

    def get_binary_expression(self):
        return self.opt_type_b + num2bytes(self.opt_value_len,1) + self.opt_value_b

class OptionalParameters(list[OptionalParameterElem], BinaryField):
    """
    The BGP OPEN message element: Optional Parameters
    """
    def __new__(cls, value):
        """
        Only validation check in this method. 
        """
        if not isinstance(value, list):
            raise ValueError("Wrong initialization of `OptionalParameters`: value not a list")
        for item in value:
            if not isinstance(item, OptionalParameterElem):
                raise ValueError(f"Wrong initialization of `OptionalParameters`: {item} not a legal type")
        return super().__new__(cls, value)

    def get_binary_expression(self):
        """
        Get the binary expression of the withdrawn routes.
        """
        return b''.join(prefix.get_binary_expression() for prefix in self)
