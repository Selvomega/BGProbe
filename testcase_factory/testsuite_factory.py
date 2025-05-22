# DIY testsuites here!

from copy import deepcopy
import sys, os, subprocess, random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bgp_utils.message import OpenMessage_BFN, OpenMessage, KeepAliveMessage_BFN, KeepAliveMessage, UpdateMessageContent_BFN, UpdateMessage_BFN, UpdateMessage, WithdrawnRoutes_BFN, NLRI_BFN, PathAttributes_BFN
from bgp_utils.path_attribute import AttrType_BFN, BaseAttr_BFN, OriginType, Origin_BFN, OriginAttr_BFN, PathSegementType, PathSegmentType_BFN, PathSegmentLength_BFN, PathSegmentValue_BFN, PathSegment_BFN, ASPath_BFN, ASPathAttr_BFN, NextHop_BFN, NextHopAttr_BFN, Communities_BFN, CommunitiesAttr_BFN, MPReachNLRI_BFN, MPReachNLRIAttr_BFN, MPUnreachNLRI_BFN, MPUnreachNLRIAttr_BFN, LOCPREF_BFN, LOCPREFAttr_BFN, Arbitrary_BFN, ArbitraryAttr_BFN
from bgp_utils.basic_bfn_types import IPv4Prefix_BFN, Length_BFN
from basic_utils.binary_utils import bytes2num
from basic_utils.log_parse_utils import MrtparseEngine, ExaBGPLogEngine
from test_agent.test_suite import TestCase, Halt, TestSuite
from test_agent.test_agent import *

from test_configuration import *

from basic_utils.binary_utils import make_bytes_displayable

def probability_true(p) -> bool:
    """
    Return True with probability p
    """
    if p < 0 or p > 1:
        raise ValueError("p must be in the range of [0.0, 1.0]")
    return random.random() < p

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

############### Define some constant prefixes ###############

CONST_PREFIX = "59.66.130.0/24"

############### Define some check functions ###############

def check_crashed():
    """
    Check if the routing software has crashed.
    """
    if router_type == RouterSoftwareType.FRR:
        return FRRRouter.if_crashed()
    elif router_type == RouterSoftwareType.BIRD:
        return BIRDRouter.if_crashed()
    else:
        # This should not happen...
        raise ValueError("Unexpected type of the router interface!")

def check_message_dump_failed() -> bool:
    """
    Check if the dump of messages failed.
    ====================
    Two requirements should be satisfied: 
    1. The prefix is advertised to the ExaBGP client, which means it's accepted by the software.
    2. The prefix is not found in the dump file of BGP messages.
    """
    return not MrtparseEngine.exist_update_prefix(TEMP_MESSAGE_DUMP, CONST_PREFIX) and ExaBGPLogEngine.exist_update_prefix(TEMP_EXABGP_DUMP, CONST_PREFIX)

def check_route_dump_failed() -> bool:
    """
    Check if the dump of routes failed.
    ====================
    Two requirements should be satisfied: 
    1. The prefix is advertised to the ExaBGP client, which means it's accepted by the software.
    2. The prefix is not found in the dump file of routes.
    """
    return not MrtparseEngine.exist_route(TEMP_ROUTE_DUMP, CONST_PREFIX) and ExaBGPLogEngine.exist_update_prefix(TEMP_EXABGP_DUMP, CONST_PREFIX)

def check_all_dump_failed() -> bool:
    """
    Check if the dump of routes failed.
    ====================
    Two requirements should be satisfied: 
    1. The prefix is advertised to the ExaBGP client, which means it's accepted by the software.
    2. The prefix is not found in the dump file of routes AND BGP messages.
    """
    return check_message_dump_failed() and check_route_dump_failed()

def check_not_advertised() -> bool:
    """
    Check if the route is not advertised.
    ====================
    Two requirements should be satisfied: 
    1. The prefix is not advertised to the ExaBGP client.
    2. The prefix is found in the dump file of routes, which means it's accepted by the software..
    """
    return MrtparseEngine.exist_route(TEMP_ROUTE_DUMP, CONST_PREFIX) and not ExaBGPLogEngine.exist_update_prefix(TEMP_EXABGP_DUMP, CONST_PREFIX)

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

###### Define the router configuration ######

router_config = vanilla_router_config

###### Define the check function ######

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

###### Define the router configuration ######

router_config = vanilla_router_config

###### Define the name of the test suite ######

def check_func() -> bool:
    """
    Checks if the given route is installed in the routing table.
    """
    target_route = CONST_PREFIX
    return MrtparseEngine.exist_update_prefix(TEMP_MESSAGE_DUMP, target_route)

###### Define the testcases ######

# UPDATE message
update_message_bfn_1 = UpdateMessage_BFN.get_bfn(
    withdrawn_routes=[],
    aspath=[tester_client_asn],
    next_hop=tester_client_ip,
    nlri=[CONST_PREFIX]
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

############################################
#               test suite 2               #
############################################

"""
Test suite 
====================
# TODO
"""

###### Define the name of the test suite ######

test_suite_name = "dump_fail-random_arbitrary_attr"

###### Define the router configuration ######

router_config = vanilla_router_config

###### Define the check function ######

check_func = check_route_dump_failed

###### Define the testcases ######

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_client_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_client_ip))

# testcase list
testcase_list = []

for i in range(512):
    # Set the AttrType_BFN randomly
    attr_type_bfn = AttrType_BFN.get_bfn(
        type_code=random.randint(100,255),
        # randomly set the partial bit and the ext_len bit.
        higher_bits=[1,1,random.randint(0,1), 1],
        lower_bits=[0]*4,
    )
    if probability_true(0.5):
        # Randomly set the value field.
        bval = random.randbytes(random.randint(0,1024))
        attr_val_bfn = Arbitrary_BFN(bval)
        attr_arbitrary = ArbitraryAttr_BFN(attr_type_bfn,attr_val_bfn)
    else:
        # Randomly set the length and value field.
        attr_val_bfn = Arbitrary_BFN(b"")
        attr_arbitrary = ArbitraryAttr_BFN(attr_type_bfn,attr_val_bfn)
        attr_arbitrary.set_bval(
            attr_type_bfn.get_binary_expression()+random.randbytes(random.randint(0,64))
        )

    # UPDATE message
    update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
        withdrawn_routes=[],
        nlri=[CONST_PREFIX],
        attr_bfn_list=[
            attr_origin,
            attr_aspath,
            attr_nexthop,
            attr_arbitrary,
        ]
    )
    update_message = UpdateMessage(update_message_bfn)

    testcase_list.append(TestCase([vanilla_open_message, vanilla_keepalive_message, update_message]))

###### Compose the test suite ######

test_suite_2 = TestSuite(
    router_config=router_config,
    testcases=testcase_list,
    check_function=check_func,
    test_suite_name=test_suite_name
)


############################################
#               test suite 3               #
############################################

"""
Test suite 
====================
# TODO
"""

###### Define the name of the test suite ######

test_suite_name = "dump_message_fail-random_arbitrary_attr"

###### Define the router configuration ######

router_config = vanilla_router_config

###### Define the check function ######

check_func = check_message_dump_failed

###### Define the testcases ######

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_client_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_client_ip))

# testcase list
testcase_list = []

for i in range(512):
    # Set the AttrType_BFN randomly
    attr_type_bfn = AttrType_BFN.get_bfn(
        type_code=random.randint(100,255),
        # randomly set the partial bit and the ext_len bit.
        higher_bits=[1,1,random.randint(0,1), 1],
        lower_bits=[0]*4,
    )
    if probability_true(0.5):
        # Randomly set the value field.
        bval = random.randbytes(random.randint(0,1024))
        attr_val_bfn = Arbitrary_BFN(bval)
        attr_arbitrary = ArbitraryAttr_BFN(attr_type_bfn,attr_val_bfn)
    else:
        # Randomly set the length and value field.
        attr_val_bfn = Arbitrary_BFN(b"")
        attr_arbitrary = ArbitraryAttr_BFN(attr_type_bfn,attr_val_bfn)
        attr_arbitrary.set_bval(
            attr_type_bfn.get_binary_expression()+random.randbytes(random.randint(0,64))
        )

    # UPDATE message
    update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
        withdrawn_routes=[],
        nlri=[CONST_PREFIX],
        attr_bfn_list=[
            attr_origin,
            attr_aspath,
            attr_nexthop,
            attr_arbitrary,
        ]
    )
    update_message = UpdateMessage(update_message_bfn)

    testcase_list.append(TestCase([vanilla_open_message, vanilla_keepalive_message, update_message]))

###### Compose the test suite ######

test_suite_3 = TestSuite(
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
    test_suite_1,
    test_suite_2,
    test_suite_3,
]
