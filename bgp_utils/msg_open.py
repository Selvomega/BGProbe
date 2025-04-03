"""
BGP OPEN message.
"""

from msg_base import MessageContent, MessageType
from open_opt import OptionalParameters
from basic_types import IP
from bgp_global_var import BGP_VERSION, HOLD_TIME

class OpenMessage(MessageContent):
    """
    BGP OPEN message.
    """
    def __init__(self,
                 asn: int,
                 bgp_identifier: IP,
                 optional_parameters: OptionalParameters,
                 bgp_version: int = BGP_VERSION,
                 bgp_hold_time: int = HOLD_TIME):
        """
        Initialize the BGP OPEN message content
        """
        self.message_type = MessageType.OPEN
        self.bgp_version = bgp_version
        self.asn = asn
        self.hold_time = bgp_hold_time
        self.bgp_identifier = bgp_identifier
        self.optional_parameter_len = optional_parameters.get_binary_length()
        self.optional_parameters = optional_parameters

    def get_binary_expression(self):
        """
        Get the binary expression of the message. 
        """
        return self.binary_content
