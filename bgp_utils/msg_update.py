"""
BGP UPDATE message.
"""

from msg_base import MessageContent, MessageType
from update_attr import PathAttributes
from update_nlri import NLRI
from update_wroutes import WithdrawnRoutes
from binary_utils import *

class UpdateMessage(MessageContent):
    """
    BGP UPDATE message.
    """
    def __init__(self,
                 withdrawn_routes: WithdrawnRoutes = WithdrawnRoutes([]),
                 attributes: PathAttributes = PathAttributes([]),
                 nlri: NLRI = NLRI([])):
        """
        Initialize the BGP UPDATE message content
        """
        self.withdrawn_routes = withdrawn_routes
        self.attributes = attributes
        self.nlri = nlri
        self.withdrawn_routes_len = self.withdrawn_routes.get_binary_length()
        self.attributes_len = self.attributes.get_binary_length()
        self.message_type = MessageType.UPDATE
    
    def _update_length_value(self):
        """
        Update the length value of the message after modification.
        """
        pass

    def _update_binary_content(self):
        """
        Update the binary value of the message after modification.
        """
        pass

    def get_binary_expression(self):
        """
        Get the binary expression of the update message content. 
        """
        return b''.join(
            [
                num2bytes(self.withdrawn_routes_len, 2),
                self.withdrawn_routes.get_binary_expression(),
                num2bytes(self.attributes_len, 2),
                self.attributes.get_binary_expression(),
                self.nlri.get_binary_expression()
            ]
        )

    # TODO: 
    # `push`, `pop`, `insert`, `remove` methods of withdrawn routes, attributes, and nlri
    # Maybe more, let's just add what is needed in the future.
    # a

