"""
BGP KEEPALIVE message.
"""

from msg_base import MessageContent, MessageType

class KeepAliveMessage(MessageContent):
    """
    BGP KEEPALIVE message.
    """
    def __init__(self,
                 binary_content=b''):
        """
        Initialize the BGP UPDATE message content
        The `binary_content` should be empty.
        """
        self.message_type = MessageType.KEEPALIVE
        self.binary_content = binary_content

    def get_binary_expression(self):
        """
        Get the binary expression of the message. 
        """
        return self.binary_content
