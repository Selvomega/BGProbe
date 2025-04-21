from ..basic_types import Length_BFN, IPv4Prefix_BFN, BinaryFieldList_BFN
from ..path_attribute.attr_base import BaseAttr_BFN
from .msg_base import MessageType, MessageType_BFN, HeaderMarker_BFN, MessageContent_BFN, BaseMessage_BFN
import numpy as np

class WithdrawnRoutes_BFN(BinaryFieldList_BFN):
    """
    BGP Withdrawn Routes field in the BGP UPDATE message.
    """
    def __init__(self,
                 bfn_list : list[IPv4Prefix_BFN]):
        """Initialize by calling BinaryFieldList_BFN's `__init__` method."""
        super().__init__(bfn_list, IPv4Prefix_BFN.get_bfn_name())

class PathAttributes_BFN(BinaryFieldList_BFN):
    """
    BGP Path Attributes field in the BGP UPDATE message.
    """
    def __init__(self,
                 bfn_list : list[BaseAttr_BFN]):
        """Initialize by calling BinaryFieldList_BFN's `__init__` method."""
        super().__init__(bfn_list, BaseAttr_BFN.get_bfn_name(), BFN_type_check=False)
    
class NLRI_BFN(BinaryFieldList_BFN):
    """
    BGP Network Layer Reachability Information (NLRI) field in the BGP UPDATE message.
    """
    def __init__(self,
                 bfn_list : list[IPv4Prefix_BFN]):
        """Initialize by calling BinaryFieldList_BFN's `__init__` method."""
        super().__init__(bfn_list, IPv4Prefix_BFN.get_bfn_name())

# +-----------------------------------------------------+
# |         Withdrawn Routes Length (2 octets)          |
# +-----------------------------------------------------+
# |             Withdrawn Routes (variable)             |
# +-----------------------------------------------------+
# |       Total Path Attribute Length (2 octets)        |
# +-----------------------------------------------------+
# |             Path Attributes (variable)              |
# +-----------------------------------------------------+
# |  Network Layer Reachability Information (variable)  |
# +-----------------------------------------------------+

class UpdateMessageContent_BFN(MessageContent_BFN):
    """
    BGP UPDATE message content.
    """
    def __init__(self,
                 wroutes_len_bfn: Length_BFN,
                 wroutes_bfn: WithdrawnRoutes_BFN,
                 path_attr_len_bfn: Length_BFN,
                 path_attr_bfn: PathAttributes_BFN,
                 nlri_bfn: NLRI_BFN):
        """Initialize the BGP OPEN message content BFN."""

        ###### Basic attributes ######

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(UpdateMessageContent_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        # No special attributes

        ###### Deal with relations with and between children ######

        # Initialize the children. 
        # The sequence is very important.
        # Parents can still be `None`
        self.wroutes_len_key = self.append_child(wroutes_len_bfn)
        self.wroutes_key = self.append_child(wroutes_bfn)
        self.path_attr_len_key = self.append_child(path_attr_len_bfn)
        self.path_attr_key = self.append_child(path_attr_bfn)
        self.nlri_key = self.append_child(nlri_bfn)
        # Update the detach state of the current BFN.
        self.detach_according_to_children()
        # Add dependencies between children
        self.add_dependency_between_children(dependent_key=self.wroutes_len_key,
                                             dependency_key=self.wroutes_key)
        self.add_dependency_between_children(dependent_key=self.path_attr_len_key,
                                             dependency_key=self.path_attr_key)
        # Let children update
        self.children_update()

    @classmethod
    def get_bfn_name() -> str:
        """Get the name of the BFN."""
        return "UpdateMessageContent_BFN"
    
    ########## Get binary info ##########

    # Use methods from father class
    
    ########## Update according to dependencies ##########
    
    # Use methods from father class

    ########## Methods for generating random mutation ##########

    # Use methods from father class

    ########## Methods for applying mutation ##########

    # The following methods are recursively calling set-function of childrens, 
    # so there is no need to use `set_function_decorator`

    def set_wroutes_len(self, length: int):
        """Set the length of Withdrawn Routes field."""
        bfn: Length_BFN = self.children[self.wroutes_len_key]
        bfn.set_length(length)

    def set_wroutes(self, wroutes: list[str]):
        """Set the Withdrawn Routes field."""
        # TODO: finish the generate instance method for IPv4Prefix_BFN first.
    
    def set_path_attr_len(self, length: int):
        """Set the length of Path Attributes field."""
        bfn: Length_BFN = self.children[self.path_attr_len_key]
        bfn.set_length(length)
    
    def set_nlri(self, nlri: list[str]):
        """Set the NLRI field."""
        # TODO: finish the generate instance method for IPv4Prefix_BFN first.
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = MessageContent_BFN.mutation_set

class UpdateMessage_BFN(BaseMessage_BFN):
    """
    BGP UPDATE message.
    """
    def __init__(self,
                 message_content_bfn: UpdateMessageContent_BFN,
                 header_marker_bfn: HeaderMarker_BFN = HeaderMarker_BFN(),
                 length_bfn: Length_BFN = Length_BFN(length_val=23,
                                                     length_byte_len=2,
                                                     include_myself=True),):
        """Initialize the BGP UPDATE message."""

        super().__init__(message_type_bfn=MessageType_BFN(MessageType.OPEN),
                         message_content_bfn=message_content_bfn,
                         header_marker_bfn=header_marker_bfn,
                         length_bfn = length_bfn)

        ###### Set the weights ######
        self.weights = np.ones(len(UpdateMessage_BFN.mutation_set))
        self.weights /= np.sum(self.weights)
    
    @classmethod
    def get_bfn_name() -> str:
        """Get the name of the BFN."""
        return "UpdateMessage_BFN"

    ########## Get binary info ##########

    # Use methods from father class

    ########## Update according to dependencies ##########
    
    # Use methods from father class

    ########## Methods for generating random mutation ##########

    # Use methods from father class

    ########## Methods for applying mutation ##########

    # The following methods are recursively calling set-function of childrens, 
    # so there is no need to use `set_function_decorator`

    def set_wroutes_len(self, length: int):
        """Set the length of Withdrawn Routes field."""
        bfn : UpdateMessage_BFN = self.children[self.message_content_key]
        bfn.set_wroutes_len(length)
    
    def set_wroutes(self, wroutes: list[str]):
        """Set the Withdrawn Routes field."""
        bfn : UpdateMessage_BFN = self.children[self.message_content_key]
        bfn.set_wroutes(wroutes)
    
    def set_path_attr_len(self, length: int):
        """Set the length of Path Attributes field."""
        bfn : UpdateMessage_BFN = self.children[self.message_content_key]
        bfn.set_path_attr_len(length)
    
    def set_nlri(self, nlri: list[str]):
        """Set the NLRI field."""
        bfn : UpdateMessage_BFN = self.children[self.message_content_key]
        bfn.set_nlri(nlri)
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BaseMessage_BFN.mutation_set
