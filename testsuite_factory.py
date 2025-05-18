# DIY testsuites here!

from copy import deepcopy
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bgp_utils.message import OpenMessage_BFN, OpenMessage, KeepAliveMessage_BFN, KeepAliveMessage, UpdateMessageContent_BFN, UpdateMessage_BFN, UpdateMessage, WithdrawnRoutes_BFN, NLRI_BFN, PathAttributes_BFN
from bgp_utils.path_attribute import AttrType_BFN, BaseAttr_BFN, OriginType, Origin_BFN, OriginAttr_BFN, PathSegementType, PathSegmentType_BFN, PathSegmentLength_BFN, PathSegmentValue_BFN, PathSegment_BFN, ASPath_BFN, ASPathAttr_BFN, NextHop_BFN, NextHopAttr_BFN, Communities_BFN, CommunitiesAttr_BFN, MPReachNLRI_BFN, MPReachNLRIAttr_BFN, MPUnreachNLRI_BFN, MPUnreachNLRIAttr_BFN, LOCPREF_BFN, LOCPREFAttr_BFN, Arbitrary_BFN, ArbitraryAttr_BFN
from bgp_utils.basic_bfn_types import IPv4Prefix_BFN, Length_BFN
from basic_utils.binary_utils import bytes2num
from test_agent.test_suite import TestCase, Halt, TestSuite

from test_configuration import *

############### Vanilla messages ###############

# Vanilla OPEN message
open_message_bfn = OpenMessage_BFN.get_bfn(BGP_CONFIG)
vanilla_open_message = OpenMessage(open_message_bfn)

# Vanilla KEEPALIVE message
keepalive_message_bfn = KeepAliveMessage_BFN.get_bfn()
vanilla_keepalive_message = KeepAliveMessage(keepalive_message_bfn)

############### Vanilla router configuration ###############

vanilla_router_config = RouterConfiguration(
    asn=router_software_asn,
    router_id=router_software_ip,
    neighbors=[
        Neighbor(
            peer_ip=tester_client_ip,
            peer_asn=tester_client_asn,
            local_source=router_software["veth"]
        ),
        Neighbor(
            peer_ip=exabgp_client_ip,
            peer_asn=exabgp_client_asn,
            local_source=router_software["veth"]
        ),
    ],
    router_type=router_type
)

############################################
#               test suite 0               #
############################################

"""
Vanilla test suite
====================
- empty UPDATE messages
- `check_func` always return `True`
"""

###### Define the name of the test suite ######

test_suite_name = "vanilla_test_suite_1"

###### Define the name of the test suite ######

router_config = vanilla_router_config

###### Define the name of the test suite ######

def check_func() -> bool:
    """
    Always return `True`
    """
    return True

###### Define the testcases ######

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_empty_message_bfn()
update_message = UpdateMessage(update_message_bfn)
# testcase
testcase = TestCase(
    [vanilla_open_message, vanilla_keepalive_message, update_message]
)
# testcase list
testcase_list = [testcase]*4

###### Compose the test suite ######

test_suite_0 = TestSuite(
    router_config=router_config,
    testcases=testcase_list,
    check_function=check_func,
    test_suite_name=test_suite_name
)

############################################
#               test suite 1               #
############################################

"""
Vanilla test suite
====================
- `check_func` checks if the given route is installed in the routing table
- To check if `check_func` can work properly. 
"""

###### Define the name of the test suite ######

test_suite_name = "vanilla_test_suite_2"

###### Define the name of the test suite ######

router_config = vanilla_router_config

###### Define the name of the test suite ######

def check_func() -> bool:
    """
    Checks if the given route is installed in the routing table.
    """
    target_route = "59.66.130.0/24"
    # TODO

###### Define the testcases ######

# UPDATE message
update_message_bfn_1 = UpdateMessage_BFN.get_bfn(
    withdrawn_routes=[],
    aspath=[tester_client_asn],
    next_hop=tester_client_ip,
    nlri=["59.66.130.0/24"]
)
update_message_bfn_2 = UpdateMessage_BFN.get_bfn(
    withdrawn_routes=[],
    aspath=[tester_client_asn],
    next_hop=tester_client_ip,
    nlri=["59.66.131.0/24"]
)
update_message_1 = UpdateMessage(update_message_bfn_1)
update_message_2 = UpdateMessage(update_message_bfn_2)
# testcase
testcase_1 = TestCase(
    [vanilla_open_message, vanilla_keepalive_message, update_message_1]
)
testcase_2 = TestCase(
    [vanilla_open_message, vanilla_keepalive_message, update_message_2]
)
# testcase list
testcase_list = [testcase_1, testcase_2]

###### Compose the test suite ######

test_suite_1 = TestSuite(
    router_config=router_config,
    testcases=testcase_list,
    check_function=check_func,
    test_suite_name=test_suite_name
)



###############################################################
#                       Test Suite List                       #
###############################################################

test_suite_list = [
    test_suite_0,
]
