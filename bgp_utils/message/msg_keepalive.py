from ..basic_bfn_types import Length_BFN
from .msg_base import MessageType, MessageType_BFN, HeaderMarker_BFN, MessageContent_BFN, BaseMessage_BFN, Message
import numpy as np

# A KEEPALIVE message consists of only the message header 
# and has a length of 19 octets.

class KeepAliveMessageContent_BFN(MessageContent_BFN):
    """
    BGP OPEN message content.
    """
    def __init__(self):
        """Initialize the BGP OPEN message content BFN."""
        
        ###### Basic attributes ######

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(KeepAliveMessageContent_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        # No special attributes

    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "KeepAliveMessageContent_BFN"

    ########## Get binary info ##########

    # Use methods from father class
    
    ########## Update according to dependencies ##########
    
    # Use methods from father class
    
    ########## Methods for generating random mutation ##########

    # Use methods from father class

    ########## Methods for applying mutation ##########

    # Use methods from father class
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = MessageContent_BFN.mutation_set

class KeepAliveMessage_BFN(BaseMessage_BFN):
    """
    BGP KEEPALIVE message.
    """

    def __init__(self,
                 message_content_bfn: KeepAliveMessageContent_BFN = KeepAliveMessageContent_BFN(),
                 header_marker_bfn: HeaderMarker_BFN = None,
                 length_bfn: Length_BFN = None,):
        """Initialize the BGP OPEN message."""

        ###### Redefine default input parameters to avoid shallow-copy ######

        if header_marker_bfn is None:
            header_marker_bfn = HeaderMarker_BFN()
            
        if length_bfn is None:
            length_bfn = Length_BFN(length_val=19,
                                    length_byte_len=2,
                                    include_myself=True)

        ###### Basic attributes ######

        super().__init__(message_type_bfn=MessageType_BFN(MessageType.KEEPALIVE),
                         message_content_bfn=message_content_bfn,
                         header_marker_bfn=header_marker_bfn,
                         length_bfn = length_bfn)

        ###### Set the weights ######
        self.weights = np.ones(len(KeepAliveMessage_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "KeepAliveMessage_BFN"

    ########## Factory methods: Create an instance of the class ##########

    @classmethod
    def get_bfn(cls):
        """
        Get the KEEPALIVE message BFN from the BGP configuration.
        """
        return KeepAliveMessage_BFN()

    ########## Get binary info ##########

    # Use methods from father class

    ########## Update according to dependencies ##########
    
    # Use methods from father class

    ########## Methods for generating random mutation ##########

    # Use methods from father class

    ########## Methods for applying mutation ##########

    # Use methods from father class
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BaseMessage_BFN.mutation_set

class KeepAliveMessage(Message):
    """
    BGP KEEPALIVE message. 
    """
    def __init__(self, message_bfn: KeepAliveMessage_BFN):
        """Initialize the BGP KEEPALIVE message"""
        super().__init__(message_bfn)

    def get_message_type(self):
        """Return the type of the message."""
        return MessageType.KEEPALIVE
