# DIY testcases here!

from copy import deepcopy
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bgp_utils.message import OpenMessage_BFN, OpenMessage, KeepAliveMessage_BFN, KeepAliveMessage, UpdateMessage_BFN, UpdateMessage
from test_agent.test_suite import TestCase

from test_configuration import *

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
    aspath=[tester_client_asn],
    next_hop=tester_client_ip,
    nlri=["59.66.130.0/24"]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_2 = TestCase([open_message, keepalive_message, update_message])

############### testcase 3 ###############

"""Testcase: Unmatched next-hop"""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn(
    withdrawn_routes=[],
    aspath=[tester_client_asn],
    next_hop="10.1.1.1", # Unmatched NEXT_HOP attribute.
    nlri=["59.66.130.0/24"]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_3 = TestCase([open_message, keepalive_message, update_message])

############### testcase 4 ###############

"""Testcase: Unmatched last AS number"""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn(
    withdrawn_routes=[],
    aspath=[1145, tester_client_asn],
    next_hop=tester_client_ip, # Unmatched NEXT_HOP attribute.
    nlri=["59.66.130.0/24"]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_4 = TestCase([open_message, keepalive_message, update_message])

############### testcase 4 ###############

"""Testcase: UPDATE message without ORIGIN attribute"""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# TODO: continue here.
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn(
    withdrawn_routes=[],
    aspath=[1145, tester_client_asn],
    next_hop=tester_client_ip, # Unmatched NEXT_HOP attribute.
    nlri=["59.66.130.0/24"]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_4 = TestCase([open_message, keepalive_message, update_message])
