from .binary_field_node import BinaryFieldNode
from .basic_types import Length_BFN
from data_utils.binary_utils import num2bytes
from enum import Enum
from functools import partial
import random
import numpy as np

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

class HeaderMarker_BFN(BinaryFieldNode):
    """
    BGP message header marker field.
    """
    def __init__(self):
        """
        Initialize the BGP message header marker BFN. 
        """
        
        ###### Basic attributes ######

        self.children : dict[str,BinaryFieldNode] = {}
        self.parent : BinaryFieldNode = None
        self.dependencies = dict[str,BinaryFieldNode] = {}
        self.depend_on_me = dict[str,BinaryFieldNode] = {}
        self.detached = False
        self.binary_content : bytes = None
        self.prefix : bytes = b''
        self.suffix : bytes = b''

        # Initialize all weights to 1.
        # IMPORTANT: use the `mutation_set` of current class!
        self.weights = np.ones(len(HeaderMarker_BFN.mutation_set))
        # Normalize
        self.weights /= np.sum(self.weights)
        # Set the learning rate.
        self.eta = 0.05

        ###### special attributes ######

        # No special attributes

    ########## Get binary info ##########

    def get_binary_expression_inner(self):
        """Get binary expression."""
        return b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'

    ########## Update according to dependencies ##########
    
    def update_on_dependencies_inner(self):
        """
        Update the current BFN according to its dependencies.
        This BFN do not have dependencies.
        """
        # You should not raise error because of `attach` function
        return

    ########## Methods for generating random mutation ##########

    # No such methods, use methods from father class

    ########## Methods for applying mutation ##########

    # No such methods, use methods from father class

    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set

class MessageType_BFN(BinaryFieldNode):
    """
    BGP message type field.
    """
    def __init__(self,
                 message_type : MessageType = MessageType.UNDEFINED):
        """
        Initialize the BGP message header marker BFN. 
        """

        ###### Basic attributes ######

        self.children : dict[str,BinaryFieldNode] = {}
        self.parent : BinaryFieldNode = None
        self.dependencies = dict[str,BinaryFieldNode] = {}
        self.depend_on_me = dict[str,BinaryFieldNode] = {}
        self.detached = False
        self.binary_content : bytes = None
        self.prefix : bytes = b''
        self.suffix : bytes = b''

        # Initialize all weights to 1.
        # IMPORTANT: use the `mutation_set` of current class!
        self.weights = np.ones(len(HeaderMarker_BFN.mutation_set))
        # Normalize
        self.weights /= np.sum(self.weights)
        # Set the learning rate.
        self.eta = 0.05

        ###### special attributes ######

        self.message_type = message_type
    
    ########## Get binary info ##########

    def get_binary_expression_inner(self):
        """Get binary expression."""
        return num2bytes(self.message_type.value, 1)

    ########## Update according to dependencies ##########
    
    def update_on_dependencies_inner(self):
        """
        Update the current BFN according to its dependencies.
        This BFN do not have dependencies.
        """
        # You should not raise error because of `attach` function
        return

    ########## Methods for generating random mutation ##########

    def random_message_type(self):
        """
        Return a random message type.
        The returned value is guaranteed to be a message type.
        """
        valid_message_types = [
            member for member in MessageType if member != MessageType.UNDEFINED
        ]
        return random.choice(valid_message_types)

    ########## Methods for applying mutation ##########

    @BinaryFieldNode.set_function_decorator
    def set_message_type(self, message_type: MessageType):
        """
        Set the message type of current BFN.
        """
        self.message_type = message_type

    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set + [
        BinaryFieldNode.MutationItem(random_message_type, set_message_type),
        BinaryFieldNode.MutationItem(
            partial(BinaryFieldNode.random_bval_fixed_len, 
                    length=1), 
            BinaryFieldNode.set_bval
        )
    ]

MessageContent_BFN = BinaryFieldNode

class BGPMessage(BinaryFieldNode):
    """
    BGP Message.
    The top level of BinaryFieldNode.
    This can be inherited by more specific message types. 
    """
    def __init__(self,
                 header_marker_bfn: HeaderMarker_BFN,
                 length_bfn: Length_BFN,
                 message_type_bfn: MessageType_BFN,
                 message_content_bfn: MessageContent_BFN): 
        """Initialize the BGP message."""

        ###### Basic attributes ######
        
        # `include_myself` have to be set True here
        length_bfn.include_myself = True

        self.children : dict[str,BinaryFieldNode] = {
            "header_marker": header_marker_bfn,
            # TODO
        }
        self.parent : BinaryFieldNode = None
        self.dependencies = dict[str,BinaryFieldNode] = {}
        self.depend_on_me = dict[str,BinaryFieldNode] = {}
        self.detached = False
        self.binary_content : bytes = None
        self.prefix : bytes = b''
        self.suffix : bytes = b''