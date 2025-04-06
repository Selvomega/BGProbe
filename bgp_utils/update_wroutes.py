"""
The withdrawn routes element of UPDATE message.
"""

from .basic_types import IPPrefix, BinaryField

class WithdrawnRoutes(list[IPPrefix], BinaryField):
    """
    The BGP UPDATE message element: Withdrawn Routes
    """
    def __new__(cls, value):
        """
        Only validation check in this method. 
        """
        if not isinstance(value, list):
            raise ValueError("Wrong initialization of `WithdrawnRoutes`: value not a list")
        for item in value:
            if not isinstance(item, IPPrefix):
                raise ValueError(f"Wrong initialization of `WithdrawnRoutes`: {item} not a legal type")
        return super().__new__(cls, value)

    def get_binary_expression(self):
        """
        Get the binary expression of the withdrawn routes.
        """
        return b''.join(prefix.get_binary_expression() for prefix in self)
