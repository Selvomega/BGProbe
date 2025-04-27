from ..binary_field_node import BinaryFieldNode
from ..basic_bfn_types import Number_BFN, ASN_BFN, Length_BFN, IPv4Address_BFN, BinaryFieldList_BFN
from ..bgp_configuration import BGP_Configuration
from .msg_base import MessageType, MessageType_BFN, HeaderMarker_BFN, MessageContent_BFN, BaseMessage_BFN, Message
from basic_utils.binary_utils import num2bytes
from enum import Enum
from functools import partial
import random
import numpy as np

class OptParmType(Enum):
    """
    Optional parameter type.
    """
    UNDEFINED = -1
    CAPABILITY = 2

class OptParmValue(Enum):
    """
    Some ready-to-use optional parameter values.
    """
    UNDEFINED = b'\xff\xff'
    MP_BGP_IPV4 = b'\x01\x04\x00\x01\x00\x01'
    ROUTE_REFRESH = b'\x02\x00'
    ENHANCED_ROUTE_REFRESH = b'\x46\x00'
    GRACEFUL_RESTART = b'\x40\x00'
    EXTENDED_MESSAGE = b'\x06\x00'

class BGPVersion_BFN(Number_BFN):
    """
    The BGP version field.
    """
    def __init__(self,
                 version_num : int = 4):
        """Initialize the BGP version BFN."""

        ###### Basic attributes ######

        super().__init__(num_val=version_num, num_len=1)

        ###### Set the weights ######
        self.weights = np.ones(len(BGPVersion_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        # No special attributes
        # Defined in `Number_BFN`
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "BGPVersion_BFN"
    
    ########## Get binary info ##########

    # Defined in `Number_BFN`

    ########## Update according to dependencies ##########
    
    # Defined in `Number_BFN`

    ########## Methods for generating random mutation ##########

    def random_version_num(self):
        """
        Return a random BGP version number.
        Just an encapsulation of the father class' method. 
        """
        return self.random_num()

    ########## Methods for applying mutation ##########

    def set_version_num(self, version_num: int):
        """
        Set the BGP version number of current BFN.
        Just an encapsulation of the father class' method. 
        So there is NO decorator. 
        """
        self.set_num(version_num)
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = Number_BFN.mutation_set

class HoldTime_BFN(Number_BFN):
    """
    The BGP hold time field.
    """
    def __init__(self,
                 hold_time : int = 180):
        """Initialize the BGP hold time BFN."""

        ###### Basic attributes ######

        super().__init__(num_val=hold_time, num_len=2)

        ###### Set the weights ######
        self.weights = np.ones(len(HoldTime_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        # No special attributes
        # Defined in `Number_BFN`
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "HoldTime_BFN"
    
    ########## Get binary info ##########

    # Defined in `Number_BFN`

    ########## Update according to dependencies ##########
    
    # Defined in `Number_BFN`

    ########## Methods for generating random mutation ##########

    def random_hold_time(self):
        """
        Return a random BGP hold time.
        Just an encapsulation of the father class' method. 
        """
        return self.random_num()

    ########## Methods for applying mutation ##########

    def set_hold_time(self, hold_time: int):
        """
        Set the BGP hold time of current BFN.
        Just an encapsulation of the father class' method. 
        So there is NO decorator. 
        """
        self.set_num(hold_time)
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = Number_BFN.mutation_set

class OpenOptParmType_BFN(BinaryFieldNode):
    """
    BGP Open Message optional parameter type.
    """
    def __init__(self,
                 opt_parm_type : OptParmType = OptParmType.UNDEFINED):
        """
        Initialize the BGP OPEN message optional parameter type BFN. 
        """

        ###### Basic attributes ######

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(OpenOptParmType_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        self.opt_parm_type = opt_parm_type

    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "OpenOptParmType_BFN"

    ########## Get binary info ##########

    def get_binary_expression_inner(self):
        """Get binary expression."""
        return num2bytes(self.opt_parm_type.value, 1)

    ########## Update according to dependencies ##########
    
    def update_on_dependencies_inner(self):
        """
        Update the current BFN according to its dependencies.
        This BFN do not have dependencies.
        """
        # You should not raise error because of `attach` function
        return
    
    ########## Methods for generating random mutation ##########

    def random_opt_parm_type(self):
        """
        Return a random optional parameter type.
        The returned value is guaranteed to be a valid optional parameter type.
        """
        # TODO: Current will only return `OptParmType.CAPABILITY`!
        valid_opt_parm_types = [
            member for member in OptParmType if member != OptParmType.UNDEFINED
        ]
        return random.choice(valid_opt_parm_types)
    
    ########## Methods for applying mutation ##########

    @BinaryFieldNode.set_function_decorator
    def set_opt_parm_type(self, opt_parm_type: OptParmType):
        """
        Set the optional parameter type of current BFN.
        """
        self.opt_parm_type = opt_parm_type
    
    @BinaryFieldNode.set_function_decorator
    def set_opt_parm_type_val(self, opt_parm_type_val: bytes):
        """
        Set the optional paramter type value of current BFN.
        Will set the binary content directly.
        But this is still not equivalent to the `set_bval` function,
        because of the overwriting rules. 
        """
        self.binary_content = opt_parm_type_val
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set + [
        # TODO: Current `random_opt_parm_type` will only return `OptParmType.CAPABILITY`!
        # BinaryFieldNode.MutationItem(random_opt_parm_type, set_opt_parm_type),
        BinaryFieldNode.MutationItem(
            partial(BinaryFieldNode.random_bval_fixed_len, 
                    length=1),
            set_opt_parm_type_val
        )
    ]

class OpenOptParmValue_BFN(BinaryFieldNode):
    """
    BGP Open Message optional parameter value.
    """
    def __init__(self,
                 opt_parm_val: OptParmValue = OptParmValue.UNDEFINED):
        """
        Initialize the BGP OPEN message optional parameter value BFN. 
        """

        ###### Basic attributes ######

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(OpenOptParmValue_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        self.opt_parm_val : OptParmValue = opt_parm_val
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "OpenOptParmValue_BFN"

    ########## Get binary info ##########

    def get_binary_expression_inner(self):
        """Get binary expression."""
        return self.opt_parm_val.value
    
    ########## Update according to dependencies ##########
    
    def update_on_dependencies_inner(self):
        """
        Update the current BFN according to its dependencies.
        This BFN do not have dependencies.
        """
        # You should not raise error because of `attach` function
        return
    
    ########## Methods for generating random mutation ##########

    def random_opt_parm_val(self):
        """
        Return a random optional parameter value.
        The returned value is guaranteed to be a valid optional parameter value.
        """
        valid_message_values = [
            member for member in OptParmValue if member != OptParmValue.UNDEFINED
        ]
        return random.choice(valid_message_values)

    ########## Methods for applying mutation ##########

    @BinaryFieldNode.set_function_decorator
    def set_opt_parm_val(self, opt_parm_val: OptParmValue):
        """
        Set the optional parameter type of current BFN.
        """
        self.opt_parm_val = opt_parm_val
    
    @BinaryFieldNode.set_function_decorator
    def set_opt_parm_val_val(self, opt_parm_val_val: bytes):
        """
        Set the optional paramter value's value of current BFN.
        Will set the binary content directly.
        But this is still not equivalent to the `set_bval` function,
        because of the overwriting rules. 
        """
        self.binary_content = opt_parm_val_val
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set + [
        BinaryFieldNode.MutationItem(random_opt_parm_val, set_opt_parm_val),
        BinaryFieldNode.MutationItem(BinaryFieldNode.random_bval,set_opt_parm_val_val)
    ]

# 0               1
# 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-...
# |  Parm. Type   | Parm. Length  | Parameter Value (variable)
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-...

class OpenOptParm_BFN(BinaryFieldNode):
    """
    BGP Open Message optional parameter.
    """
    def __init__(self,
                 opt_parm_type: OpenOptParmType_BFN,
                 opt_parm_val: OpenOptParmValue_BFN,
                 opt_parm_len: Length_BFN = None):
        "Initialize the BGP OPEN message optional parameter BFN."

        ###### Redefine default input parameters to avoid shallow-copy ######

        if opt_parm_len is None:
            opt_parm_len = Length_BFN(length_val=0,
                                      length_byte_len=1,
                                      include_myself=False)
        
        ###### Basic attributes ######

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(OpenOptParm_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        # No special attributes

        ###### Deal with relations with and between children ######

        # Initialize the children. 
        # The sequence is very important.
        # Parents can still be `None`
        self.opt_parm_type_key = self.append_child(opt_parm_type)
        self.opt_parm_len_key = self.append_child(opt_parm_len)
        self.opt_parm_val_key = self.append_child(opt_parm_val)
        # Update the detach state of the current BFN.
        self.detach_according_to_children()
        # Add dependencies between children
        self.add_dependency_between_children(dependent_key=self.opt_parm_len_key,
                                             dependency_key=self.opt_parm_val_key)
        # Let children update
        self.children_update()
        # print(f"For debug: Optional parameter len - {self.children[self.opt_parm_len_key].num_val}, {self.children[self.opt_parm_len_key].get_binary_expression()}, {self.children}")

    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "OpenOptParm_BFN"

    ########## Factory methods: Create an instance of the class ##########

    @classmethod
    def get_capability_bfn(cls, capability_val: OptParmValue):
        """Get the OpenOptParm_BFN from the optional parameter value."""
        return OpenOptParm_BFN(
            opt_parm_type=OpenOptParmType_BFN(OptParmType.CAPABILITY),
            opt_parm_val=OpenOptParmValue_BFN(capability_val),
            opt_parm_len=Length_BFN(length_val=0, length_byte_len=1, include_myself=False)
        )

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
        Set the length of the OPEN optional parameter BFN.
        """
        bfn : Length_BFN = self.children[self.opt_parm_len_key]
        bfn.set_length(length_val)
    
    def set_opt_parm_type(self, opt_parm_type: OptParmType):
        """
        Set the type of the OPEN optional parameter BFN.
        """
        bfn : OpenOptParmType_BFN = self.children[self.opt_parm_type_key]
        bfn.set_opt_parm_type(opt_parm_type)
    
    def set_opt_parm_val_bval(self, opt_parm_val_bval: bytes):
        """
        Set the header marker of the Message BFN.
        """
        bfn : OpenOptParmValue_BFN = self.children[self.opt_parm_val_key]
        bfn.set_bval(opt_parm_val_bval)
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set

class OpenOptParmList_BFN(BinaryFieldList_BFN):
    """
    BGP Open Message optional parameter list.
    When inheriting `BinaryFieldList_BFN`, only need to rewrite the `__init__` method
    """
    def __init__(self, 
                 bfn_list : list[OpenOptParm_BFN]):
        """Initialize by calling BinaryFieldList_BFN's `__init__` method."""
        super().__init__(bfn_list, OpenOptParm_BFN.get_bfn_name())
    

# 0                   1                   2                   3
# 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
# +-+-+-+-+-+-+-+-+
# |    Version    |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |     My Autonomous System      |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |           Hold Time           |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                        BGP Identifier                         |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# | Opt Parm Len  |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                                                               |
# |                Optional Parameters (variable)                 |
# |                                                               |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

class OpenMessageContent_BFN(MessageContent_BFN):
    """
    BGP OPEN message content.
    """
    def __init__(self,
                 bgp_version_bfn: BGPVersion_BFN,
                 asn_bfn: ASN_BFN,
                 hold_time_bfn: HoldTime_BFN,
                 bgp_identifier_bfn: IPv4Address_BFN,
                 opt_parm_len_bfn: Length_BFN = None,
                 opt_parm_bfn: OpenOptParmList_BFN = None):
        """Initialize the BGP OPEN message content BFN."""

        ###### Redefine default input parameters to avoid shallow-copy ######

        if opt_parm_len_bfn is None:
            opt_parm_len_bfn = Length_BFN(length_val=0, length_byte_len=1)
        
        if opt_parm_bfn is None:
            opt_parm_bfn = OpenOptParmList_BFN([])

        ###### Basic attributes ######

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(OpenMessageContent_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        # No special attributes

        ###### Deal with relations with and between children ######

        # Initialize the children. 
        # The sequence is very important.
        # Parents can still be `None`
        self.bgp_version_key = self.append_child(bgp_version_bfn)
        self.asn_key = self.append_child(asn_bfn)
        self.hold_time_key = self.append_child(hold_time_bfn)
        self.bgp_identifier_key = self.append_child(bgp_identifier_bfn)
        self.opt_parm_len_key = self.append_child(opt_parm_len_bfn)
        self.opt_parm_key = self.append_child(opt_parm_bfn)
        # Update the detach state of the current BFN.
        self.detach_according_to_children()
        # Add dependencies between children
        self.add_dependency_between_children(dependent_key=self.opt_parm_len_key,
                                             dependency_key=self.opt_parm_key)
        # Let children update
        self.children_update()

    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "OpenMessageContent_BFN"

    ########## Get binary info ##########

    # Use methods from father class
    
    ########## Update according to dependencies ##########
    
    # Use methods from father class
    
    ########## Methods for generating random mutation ##########

    # Use methods from father class

    ########## Methods for applying mutation ##########

    # The following methods are recursively calling set-function of childrens, 
    # so there is no need to use `set_function_decorator`

    def set_bgp_version(self, bgp_version_num: int):
        """
        Set the BGP version of the BGP OPEN message content.
        """
        bfn : BGPVersion_BFN = self.children[self.bgp_version_key]
        bfn.set_version_num(bgp_version_num)
    
    def set_asn(self, asn: int):
        """
        Set the AS number of the BGP OPEN message content.
        """
        bfn : ASN_BFN = self.children[self.asn_key]
        bfn.set_asn(asn)

    def set_hold_time(self, hold_time: int):
        """
        Set the hold time of the BGP OPEN message content.
        """
        bfn : HoldTime_BFN = self.children[self.hold_time_key]
        bfn.set_hold_time(hold_time)

    def set_bgp_identifier(self, bgp_identifier: str):
        """
        Set the BGP identifier of the BGP OPEN message content.
        """
        bfn : IPv4Address_BFN = self.children[self.bgp_identifier_key]
        bfn.set_ip_addr(bgp_identifier)

    def set_opt_parm_len(self, opt_parm_len: int):
        """
        Set the OPEN optional parameter length of the BGP OPEN message content.
        """
        bfn : Length_BFN = self.children[self.opt_parm_len_key]
        bfn.set_length(opt_parm_len)

    def append_opt_parm(self, opt_parm: OpenOptParm_BFN):
        """
        Append a OPEN optional parameter to the BGP OPEN message content.
        """
        bfn : OpenOptParmList_BFN = self.children[self.opt_parm_key]
        bfn.append_bfn(opt_parm)
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = MessageContent_BFN.mutation_set

class OpenMessage_BFN(BaseMessage_BFN):
    """
    BGP OPEN message.
    """

    def __init__(self,
                 message_content_bfn: OpenMessageContent_BFN,
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

        super().__init__(message_type_bfn=MessageType_BFN(MessageType.OPEN),
                         message_content_bfn=message_content_bfn,
                         header_marker_bfn=header_marker_bfn,
                         length_bfn = length_bfn)

        ###### Set the weights ######
        self.weights = np.ones(len(OpenMessage_BFN.mutation_set))
        self.weights /= np.sum(self.weights)
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "OpenMessage_BFN"
    
    ########## Factory methods: Create an instance of the class ##########

    @classmethod
    def get_bfn(cls, bgp_config: BGP_Configuration):
        """
        Get the OPEN message BFN from the BGP configuration.
        """
        candidate_list = [
            OpenOptParm_BFN.get_capability_bfn(OptParmValue.ROUTE_REFRESH),
            OpenOptParm_BFN.get_capability_bfn(OptParmValue.ENHANCED_ROUTE_REFRESH),
            OpenOptParm_BFN.get_capability_bfn(OptParmValue.EXTENDED_MESSAGE),
            OpenOptParm_BFN.get_capability_bfn(OptParmValue.GRACEFUL_RESTART)
        ]
        selection_list = [
            bgp_config.route_refresh,
            bgp_config.enhanced_route_refresh,
            bgp_config.extended_message,
            bgp_config.graceful_restart,
        ]
        opt_parm_list = [
            item for item, flag in zip(candidate_list, selection_list) if flag
        ]
        open_msg_content_bfn = OpenMessageContent_BFN(
            bgp_version_bfn=BGPVersion_BFN(bgp_config.bgp_version),
            asn_bfn=ASN_BFN(bgp_config.asn),
            hold_time_bfn=HoldTime_BFN(bgp_config.hold_time),
            bgp_identifier_bfn=IPv4Address_BFN(bgp_config.bgp_identifier),
            opt_parm_bfn=OpenOptParmList_BFN(opt_parm_list)
        )
        return OpenMessage_BFN(open_msg_content_bfn)

    ########## Get binary info ##########

    # Use methods from father class

    ########## Update according to dependencies ##########
    
    # Use methods from father class

    ########## Methods for generating random mutation ##########

    # Use methods from father class

    ########## Methods for applying mutation ##########

    # The following methods are recursively calling set-function of childrens, 
    # so there is no need to use `set_function_decorator`

    def set_bgp_version(self, bgp_version_num: int):
        """
        Set the BGP version of the BGP OPEN message content.
        """
        bfn : OpenMessageContent_BFN = self.children[self.message_content_key]
        bfn.set_bgp_version(bgp_version_num)
    
    def set_asn(self, asn: int):
        """
        Set the AS number of the BGP OPEN message content.
        """
        bfn : OpenMessageContent_BFN = self.children[self.message_content_key]
        bfn.set_asn(asn)

    def set_hold_time(self, hold_time: int):
        """
        Set the hold time of the BGP OPEN message content.
        """
        bfn : OpenMessageContent_BFN = self.children[self.message_content_key]
        bfn.set_hold_time(hold_time)

    def set_bgp_identifier(self, bgp_identifier: str):
        """
        Set the BGP identifier of the BGP OPEN message content.
        """
        bfn : OpenMessageContent_BFN = self.children[self.message_content_key]
        bfn.set_bgp_identifier(bgp_identifier)

    def set_opt_parm_len(self, opt_parm_len: int):
        """
        Set the OPEN optional parameter length of the BGP OPEN message content.
        """
        bfn : OpenMessageContent_BFN = self.children[self.message_content_key]
        bfn.set_opt_parm_len(opt_parm_len)

    def append_opt_parm(self, opt_parm: OpenOptParm_BFN):
        """
        Append a OPEN optional parameter to the BGP OPEN message content.
        """
        bfn : OpenMessageContent_BFN = self.children[self.message_content_key]
        bfn.append_opt_parm(opt_parm)
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BaseMessage_BFN.mutation_set

class OpenMessage(Message):
    """
    BGP OPEN message. 
    """
    def __init__(self, message_bfn: OpenMessage_BFN):
        """Initialize the BGP OPEN message"""
        super().__init__(message_bfn)

    def get_message_type(self):
        """Return the type of the message."""
        return MessageType.OPEN
