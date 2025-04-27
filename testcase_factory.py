# DIY testcases here!

from copy import deepcopy
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bgp_utils.message import OpenMessage_BFN, OpenMessage, KeepAliveMessage_BFN, KeepAliveMessage, UpdateMessage_BFN, UpdateMessage
from bgp_utils.bgp_configuration import BGP_Configuration, parse_bgp_config_from_yaml
from test_agent.test_agent import TestAgent
from test_agent.test_suite import TestCase, TestSuite
from network_utils.tcp_client import TCPClientConfiguration
from network_utils.utils import get_ipv4_prefix_parts
from routing_software_interface.basic_types import RouterConfiguration, RouterSoftwareType, Neighbor
from basic_utils.binary_utils import make_bytes_displayable

############### Basic configurations ###############

# Load the local network configuration, 
# which is related to the BGP software configuration
from vnet_config import VNET_CONFIG
# Software tester configuration
client = VNET_CONFIG["clients"][0]

# Load the test side configuration
BGP_CONFIG : BGP_Configuration = parse_bgp_config_from_yaml("bgp_config.yaml")
client_ip, _ = get_ipv4_prefix_parts(client['ip'])
client_identifier = BGP_CONFIG.bgp_identifier
client_asn = BGP_CONFIG.asn

# Check the consistency between `VNET_CONFIG` and `BGP_CONFIG`.
if client_ip != client_identifier:
    print(f"Warning: The BGP tester's ip ({client_ip}) and BGP identifier {client_identifier} are not consistent!")

############### Vanilla messages ###############

# Vanilla OPEN message
open_message_bfn = OpenMessage_BFN.get_bfn(BGP_CONFIG)
vanilla_open_message = OpenMessage(open_message_bfn)

# Vanilla KEEPALIVE message
keepalive_message_bfn = KeepAliveMessage_BFN.get_bfn()
vanilla_keepalive_message = KeepAliveMessage(keepalive_message_bfn)

############### testcase 0 ###############

"""Vanilla testcase: No UPDATE message."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# testcase
testcase_0 = TestCase([open_message, keepalive_message])

############### testcase 1 ###############

"""Vanilla testcase: Empty UPDATE message."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_empty_message_bfn()
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_1 = TestCase([open_message, keepalive_message, update_message])

############### testcase 2 ###############

"""Vanilla testcase: Trivial UPDATE message"""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn(
    withdrawn_routes=[],
    aspath=[client_asn],
    next_hop=client_ip,
    nlri=["59.66.130.0/24"]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_2 = TestCase([open_message, keepalive_message, update_message])
