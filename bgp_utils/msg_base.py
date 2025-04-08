from enum import Enum
from data_utils.binary_utils import *
from .basic_types import BinaryField, abstractmethod
from .bgp_global_var import *

class MessageType(Enum):
    """
    Type of BGP message.
    You cannot add other purely functional types (types without actual semantics in BGP) like `UNDEFINED`, neither can you delete `UNDEFINED`,
    since it will affect the semantic of our codes.
    """
    # Invalid message type
    UNDEFINED = -1
    OPEN = 1
    UPDATE = 2
    NOTIFICATION = 3
    KEEPALIVE = 4

class MessageContent(BinaryField):
    """
    BGP message content
    """
    def __init__(self):
        """
        Initialization
        """
        self.binary_content: bytes = None
        self.message_type: MessageType = None

    @abstractmethod
    def get_binary_expression(self):
        """
        Get the binary expression of the message. 
        """
        pass
    
    def get_binary_length(self):
        """
        Get the length of message. 
        """
        return len(self.get_binary_expression())

    def get_message_type(self):
        """
        Return the type of the message. 
        """
        return self.message_type

class Message(BinaryField):
    """
    BGP message. 
    """
    def __init__(self, message_content: MessageContent = None):
        """
        Initialize the message. 
        """
        self.header_marker = b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
        self.message_type_b: bytes = num2bytes(message_content.get_message_type().value, 1)
        # TODO urgent: fix this!
        self.message_len = message_content.get_binary_length()
        self.message_content: MessageContent = message_content

    def set_header_marker(self, self_defined:bytes):
        """
        Set the message header marker into a self-defined value.
        """
        self.header_marker = self_defined

    def set_message_type(self, input_val):
        """
        Set the message type into some other values.
        Three ways of setting the parameters:
        1. message_type: MessageType
        2. message_type_code: int
        3. self_defined: bytes
        """
        if isinstance(input_val, MessageType):
            self.message_type_b = num2bytes(input_val.value, 1)
        elif isinstance(input_val, int):
            self.message_type_b = num2bytes(input_val, 1)
        elif isinstance(input_val, bytes):
            self.message_type_b = input_val
        else:
            raise ValueError(f"Invalid input parameters: {input_val}")
        
    def set_message_length(self, length: int):
        """
        Set the length of the message.
        """
        self.message_len = length

    def get_header_marker(self):
        """
        Get the header marker of the message
        """
        return self.header_marker

    def get_message_type(self):
        """
        Get the message type
        """
        type_code: int = bytes2num(self.message_type_b)
        if type_code<=0 or type_code>=len(MessageType):
            return MessageType.UNDEFINED
        return MessageType(type_code)

    def get_message_length(self):
        """
        Return the length of the message
        """
        return self.message_len

    def get_binary_expression(self):
        """
        Get the binary expression of the message. 
        """
        return b''.join(
            [
                self.get_header_marker(),
                num2bytes(self.get_message_length()+19,2),
                num2bytes(self.get_message_type().value,1),
                self.message_content.get_binary_expression()
            ]
        )
