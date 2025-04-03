"""
BGP KEEPALIVE message.
"""

from msg_base import MessageContent, MessageType

# TODO: The implementation should be modified!
class NotificationMessage(MessageContent):
    """
    BGP NOTIFICATION message.
    """
    def __init__(self,
                 binary_content=b''):
        """
        Initialize the BGP NOTIFICATION message content
        """
        self.message_type = MessageType.NOTIFICATION
        self.binary_content = binary_content

    def get_binary_expression(self):
        """
        Get the binary expression of the message. 
        """
        return self.binary_content
