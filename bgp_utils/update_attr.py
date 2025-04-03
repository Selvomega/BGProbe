"""
The path attribute element of UPDATE message.
"""

from basic_types import BinaryField
from attr_base import BaseAttr

# from attr_aspath import *
# from attr_communities import *
# from attr_locpref import *
# from attr_med import *
# from attr_nexthop import *
# from attr_origin import *

class PathAttributes(list[BaseAttr], BinaryField):
    """
    The BGP UPDATE message element: Path Attribute
    """
    def __new__(cls, value):
        """
        Only validation check in this method. 
        """
        if not isinstance(value, list):
            raise ValueError("Wrong initialization of `PathAttributes`: value not a list")
        for item in value:
            if not isinstance(item, BaseAttr):
                raise ValueError(f"Wrong initialization of `PathAttributes`: {item} not a legal type")
        return super().__new__(cls, value)

    def get_binary_expression(self):
        """
        Get the binary expression of the path attribute.
        """
        return b''.join(attr.get_binary_expression() for attr in self)
