from ..binary_field_node import BinaryFieldNode
from ..basic_types import Length_BFN
from data_utils.binary_utils import num2bytes, bytes2num
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

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(HeaderMarker_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        # No special attributes
    
    @classmethod
    def get_bfn_name() -> str:
        """Get the name of the BFN."""
        return "HeaderMarker_BFN"

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

    # Use methods from father class

    ########## Methods for applying mutation ##########

    # Use methods from father class

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
        Initialize the BGP message type BFN. 
        """

        ###### Basic attributes ######

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(MessageType_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        self.message_type = message_type
    
    @classmethod
    def get_bfn_name() -> str:
        """Get the name of the BFN."""
        return "MessageType_BFN"
    
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

    def random_message_type(self) -> MessageType:
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
    
    @BinaryFieldNode.set_function_decorator
    def set_message_type_val(self, message_type_val: bytes):
        """
        Set the message type value of current BFN.
        Will set the binary content directly.
        But this is still not equivalent to the `set_bval` function,
        because of the overwriting rules. 
        """
        self.binary_content = message_type_val

    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set + [
        BinaryFieldNode.MutationItem(random_message_type, set_message_type),
        BinaryFieldNode.MutationItem(
            partial(BinaryFieldNode.random_bval_fixed_len, 
                    length=1), 
            set_message_type_val
        )
    ]

MessageContent_BFN = BinaryFieldNode

# 0                   1                   2                   3
# 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                                                               |
# +                                                               +
# |                                                               |
# +                                                               +
# |                            Marker                             |
# +                                                               +
# |                                                               |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |            Length            |      Type      |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

class BaseMessage_BFN(BinaryFieldNode):
    """
    BGP Base Message.
    The top level of BinaryFieldNode.
    This can be inherited by more specific message types. 
    """
    def __init__(self,
                 message_type_bfn: MessageType_BFN,
                 message_content_bfn: MessageContent_BFN,
                 header_marker_bfn: HeaderMarker_BFN = HeaderMarker_BFN(),
                 length_bfn: Length_BFN = Length_BFN(length_val=19,
                                                     length_byte_len=2,
                                                     include_myself=True),
                 ): 
        """Initialize the BGP message."""

        ###### Basic attributes ######

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(BaseMessage_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        # No special attributes

        ###### Deal with relations with and between children ######

        # Initialize the children. 
        # The sequence is very important.
        # Parents can still be `None`
        self.header_marker_key = self.append_child(header_marker_bfn)
        self.length_key = self.append_child(length_bfn)
        self.message_type_key = self.append_child(message_type_bfn)
        self.message_content_key = self.append_child(message_content_bfn)
        # Update the detach state of the current BFN.
        self.detach_according_to_children()
        # Add dependencies between children
        self.children[self.length_key].include_myself = True
        self.add_dependency_between_children(dependent_key=self.length_key,
                                             dependency_key=self.header_marker_key)
        self.add_dependency_between_children(dependent_key=self.length_key,
                                             dependency_key=self.message_type_key)
        self.add_dependency_between_children(dependent_key=self.length_key,
                                             dependency_key=self.message_content_key)
        # Let children update
        self.children_update()
    
    @classmethod
    def get_bfn_name() -> str:
        """Get the name of the BFN."""
        return "BaseMessage_BFN"

    ########## Get binary info ##########

    def get_binary_expression_inner(self):
        """Get binary expression."""
        # Concatenate the children's binary expressions.
        return b''.join([
            child.get_binary_expression() for child in self.children.values()
        ])

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

    # The following methods are recursively calling set-function of childrens, 
    # so there is no need to use `set_function_decorator`

    def set_length(self, length_val: int):
        """
        Set the length of the Message BFN.
        """
        bfn : Length_BFN = self.children[self.length_key]
        bfn.set_length(length_val)

    def set_message_type(self, message_type: MessageType):
        """
        Set the message type of the Message BFN.
        """
        bfn: MessageType_BFN = self.children[self.message_type_key]
        bfn.set_message_type(message_type)

    def set_header_marker_bval(self, header_marker: bytes):
        """
        Set the header marker of the Message BFN.
        """
        bfn : HeaderMarker_BFN = self.children[self.header_marker_key]
        bfn.set_bval(header_marker)

    def set_message_content_bval(self, message_content: bytes):
        """
        Set the header marker of the Message BFN.
        """
        bfn : MessageContent_BFN = self.children[self.message_content_key]
        bfn.set_bval(message_content)
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set
