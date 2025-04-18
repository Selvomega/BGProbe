from ..binary_field_node import BinaryFieldNode
from ..basic_types import Number_BFN, ASN_BFN, Length_BFN, IPv4Address_BFN, BinaryFieldList_BFN
from .msg_base import MessageType, MessageType_BFN, HeaderMarker_BFN, MessageContent_BFN, BaseMessage_BFN
from data_utils.binary_utils import num2bytes
from enum import Enum
from functools import partial
import random
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
    def get_bfn_name() -> str:
        """Get the name of the BFN."""
        return "KeepAliveMessageContent_BFN"

    ########## Get binary info ##########

    def get_binary_expression_inner(self):
        """Get binary expression."""
        # Return an empty byte sequence for the KEEPALIVE message.
        return b''
    
    ########## Update according to dependencies ##########
    
    def update_on_dependencies_inner(self):
        """
        Update the current BFN according to its dependencies.
        This BFN do not have dependencies.
        """
        # You should not raise error because of `attach` function
        return
    
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
                 header_marker_bfn: HeaderMarker_BFN = HeaderMarker_BFN(),
                 length_bfn: Length_BFN = Length_BFN(length_val=19,
                                                     length_byte_len=2,
                                                     include_myself=True),):
        """Initialize the BGP OPEN message."""

        super().__init__(message_type_bfn=MessageType_BFN(MessageType.OPEN),
                         message_content_bfn=message_content_bfn,
                         header_marker_bfn=header_marker_bfn,
                         length_bfn = length_bfn)

        ###### Set the weights ######
        self.weights = np.ones(len(KeepAliveMessage_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

    @classmethod
    def get_bfn_name() -> str:
        """Get the name of the BFN."""
        return "KeepAliveMessage_BFN"

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
