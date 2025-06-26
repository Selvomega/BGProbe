# DIY testcases here!

from copy import deepcopy
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bgp_toolkit.message import OpenMessage_BFN, OpenMessage, KeepAliveMessage_BFN, KeepAliveMessage, UpdateMessageContent_BFN, UpdateMessage_BFN, UpdateMessage, WithdrawnRoutes_BFN, NLRI_BFN, PathAttributes_BFN
from bgp_toolkit.path_attribute import AttrType_BFN, BaseAttr_BFN, OriginType, Origin_BFN, OriginAttr_BFN, PathSegementType, PathSegmentType_BFN, PathSegmentLength_BFN, PathSegmentValue_BFN, PathSegment_BFN, ASPath_BFN, ASPathAttr_BFN, NextHop_BFN, NextHopAttr_BFN, Communities_BFN, CommunitiesAttr_BFN, MPReachNLRI_BFN, MPReachNLRIAttr_BFN, MPUnreachNLRI_BFN, MPUnreachNLRIAttr_BFN, LOCPREF_BFN, LOCPREFAttr_BFN, Arbitrary_BFN, ArbitraryAttr_BFN
from bgp_toolkit.basic_bfn_types import IPv4Prefix_BFN, Length_BFN
from bgp_toolkit.binary_field_node import *
from basic_utils.binary_utils import bytes2num, make_bytes_displayable
from .basic_types import Halt, TestCase

from bgprobe_config import *

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

"""Vanilla testcase: Trivial UPDATE message."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn(
    withdrawn_routes=[],
    aspath=[tester_agent_asn],
    next_hop=tester_agent_ip,
    nlri=["59.66.130.0/24"]
)

update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_2 = TestCase([open_message, keepalive_message, update_message])

############### testcase 3 ###############

"""Testcase: Unmatched next-hop."""
# This is expected to be ignored but not hurt the connection

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn(
    withdrawn_routes=[],
    aspath=[tester_agent_asn],
    next_hop="10.1.1.1", # Unmatched NEXT_HOP attribute.
    nlri=["59.66.130.0/24"]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_3 = TestCase([open_message, keepalive_message, update_message])

############### testcase 4 ###############

"""Testcase: Unmatched last AS number."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn(
    withdrawn_routes=[],
    aspath=[1145, tester_agent_asn], # Unmatched AS number
    next_hop=tester_agent_ip,
    nlri=["59.66.130.0/24"]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_4 = TestCase([open_message, keepalive_message, update_message])

############### testcase 5 ###############

"""Testcase: UPDATE message lacking mandatory attribute - ORIGIN."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip))
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.130.0/24"],
    attr_bfn_list=[
        attr_aspath,
        attr_nexthop
    ] # Lacking ORIGIN path attribute
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_5 = TestCase([open_message, keepalive_message, update_message])

############### testcase 6 ###############

"""Testcase: No NLRI but still use path attributes (No MP_REACH_NLRI)."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn(
    withdrawn_routes=[],
    aspath=[tester_agent_asn],
    next_hop=tester_agent_ip,
    nlri=[] # NO NLRI attribute.
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_6 = TestCase([open_message, keepalive_message, update_message])

############### testcase 7 ###############

"""Testcase: Withdraw route that does not exist."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn(
    withdrawn_routes=["59.66.130.0/24"], # Withdrawn routes that does not exist.
    aspath=[tester_agent_asn],
    next_hop=tester_agent_ip,
    nlri=["59.66.135.0/24"]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_7 = TestCase([open_message, keepalive_message, update_message])

############### testcase 8 ###############

"""Testcase: Update message with multiple AS segments."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn(
    withdrawn_routes=[],
    aspath=([tester_agent_asn,114],[514,1919,810]),
    next_hop=tester_agent_ip,
    nlri=["59.66.130.0/24"]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_8 = TestCase([open_message, keepalive_message, update_message])

############### testcase 9 ###############

"""Testcase: Update message with AS loop."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn(
    withdrawn_routes=[],
    aspath=[tester_agent_asn,114,514,1919,114],
    next_hop=tester_agent_ip,
    nlri=["59.66.130.0/24"]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_9 = TestCase([open_message, keepalive_message, update_message])

############### testcase 10 ###############

"""Testcase: UPDATE message with out-of-order path attribute."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip))
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.130.0/24"],
    attr_bfn_list=[
        attr_nexthop,
        attr_origin,
        attr_aspath
    ] # Out-of-order path attributes
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_10 = TestCase([open_message, keepalive_message, update_message])

############### testcase 11 ###############

"""Testcase: UPDATE message with COMMUNITIES attribute."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip))
attr_communities = CommunitiesAttr_BFN.get_bfn(
    [(bytes2num(b'\xFF\xFF'), bytes2num(b'\xFF\x01'))]
)# NO_EXPORT COMMUNITIES
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.130.0/24"],
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_nexthop,
        attr_communities,
    ]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_11 = TestCase([open_message, keepalive_message, update_message])

############### testcase 12 ###############

"""Testcase: UPDATE message with unknown COMMUNITIES operation."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip))
attr_communities = CommunitiesAttr_BFN.get_bfn(
    [(router_agent_asn, 114)]
) # Unknown COMMUNITIES operation.
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.130.0/24"],
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_nexthop,
        attr_communities,
    ]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_12 = TestCase([open_message, keepalive_message, update_message])

############### testcase 13 ###############

"""Testcase: UPDATE message with unknown path attribute."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip))
attr_arbitrary = ArbitraryAttr_BFN(
    attr_type_bfn=AttrType_BFN.get_bfn(
        type_code=114, # An unknown type
        higher_bits=[1,1,1,0], # optional, transitive, partial, no extended length
    ),
    attr_value_bfn=Arbitrary_BFN(value=b'\x11\x45\x14\x19')
) # Unknown path attribute.

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.130.0/24"],
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_nexthop,
        attr_arbitrary,
    ]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_13 = TestCase([open_message, keepalive_message, update_message])

############### testcase 14 ###############

"""Testcase: UPDATE message with repeated path attribute."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
# Repeated path attrbutes.
attr_aspath_1 = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn, 114]))
attr_aspath_2 = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn, 514]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip))

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.130.0/24"],
    attr_bfn_list=[
        attr_origin,
        attr_aspath_1,
        attr_aspath_2,
        attr_nexthop,
    ]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_14 = TestCase([open_message, keepalive_message, update_message])

############### testcase 15 ###############

"""Testcase: UPDATE message with near-maximum number of AS in AS_PATH."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))

attr_aspath = ASPathAttr_BFN(
    ASPath_BFN.get_bfn(as_path=[tester_agent_asn] + [i for i in range(64000,64254)]),
    ext_len=True
) # AS_PATH with near-maximum length (one more to make the AS segment overflow).
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip))

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.130.0/24"],
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_nexthop,
    ]
)

update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_15 = TestCase([open_message, keepalive_message, update_message])

############### testcase 16 ###############

"""Testcase: UPDATE message with another AS' COMMUNITIES."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn(
    aspath=[tester_agent_asn],
    next_hop=tester_agent_ip,
    nlri=["59.66.130.0/24"],
    communities=[(114, 514)] # Another AS' COMMUNITIES
)

update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_16 = TestCase([open_message, keepalive_message, update_message])

############### testcase 17 ###############

"""Testcase: UPDATE message with multiple BGP COMMUNITIES."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn(
    aspath=[tester_agent_asn],
    next_hop=tester_agent_ip,
    nlri=["59.66.130.0/24"],
    communities=[(114, 514), (1919, 810), (250, 382)] # Multiple BGP COMMUNITIES
)

update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_17 = TestCase([open_message, keepalive_message, update_message])

############### testcase 18 ###############

"""Testcase: UPDATE message with empty COMMUNITIES list."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip))
attr_communities = CommunitiesAttr_BFN.get_bfn(
    []
) # empty COMMUNITIES list.
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.130.0/24"],
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_nexthop,
        attr_communities,
    ]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_18 = TestCase([open_message, keepalive_message, update_message])

############### testcase 19 ###############

"""Testcase: Repeated NLRI components."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn(
    aspath=[tester_agent_asn],
    next_hop=tester_agent_ip,
    nlri=["59.66.130.0/24", "59.66.130.0/24", "59.66.130.0/24"] # Repeated NLRI components.
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_19 = TestCase([open_message, keepalive_message, update_message])

############### testcase 20 ###############

"""Vanilla testcase: UPDATE message with MP_REACH_NLRI attribute."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_mpreachnlri = MPReachNLRIAttr_BFN.get_ipv4_unicast_bfn(
    mp_nexthop=tester_agent_ip,
    mp_nlri=["59.66.130.0/24"]
)
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=[], # NLRI is left empty
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_mpreachnlri
    ] # MP_REACH_NLRI and no NEXT_HOP
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_20 = TestCase([open_message, keepalive_message, update_message])

############### testcase 21 ###############

"""Testcase: UPDATE message with all NLRI, NEXT_HOP and MP_REACH_NLRI attribute."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip))
attr_mpreachnlri = MPReachNLRIAttr_BFN.get_ipv4_unicast_bfn(
    mp_nexthop=tester_agent_ip,
    mp_nlri=["59.66.130.0/24"]
)
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.131.0/24"],
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_nexthop,
        attr_mpreachnlri
    ] # MP_REACH_NLRI and NEXT_HOP
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_21 = TestCase([open_message, keepalive_message, update_message])

############### testcase 22 ###############

"""Testcase: UPDATE message with multiple IPv4 unicast MP_REACH_NLRI attribute."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_mpreachnlri_0 = MPReachNLRIAttr_BFN.get_ipv4_unicast_bfn(
    mp_nexthop=tester_agent_ip,
    mp_nlri=["59.66.130.0/24"]
)
attr_mpreachnlri_1 = MPReachNLRIAttr_BFN.get_ipv4_unicast_bfn(
    mp_nexthop=tester_agent_ip,
    mp_nlri=["59.66.131.0/24"]
)
attr_mpreachnlri_2 = MPReachNLRIAttr_BFN.get_ipv4_unicast_bfn(
    mp_nexthop=tester_agent_ip,
    mp_nlri=["59.66.132.0/24"]
)
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=[], # NLRI is left empty
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_mpreachnlri_0,
        attr_mpreachnlri_1,
        attr_mpreachnlri_2,
    ] # multiple MP_REACH_NLRI with the same type
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_22 = TestCase([open_message, keepalive_message, update_message])

############### testcase 23 ###############

"""Testcase: No NLRI but still use path attributes (With MP_REACH_NLRI)."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip))
attr_mpreachnlri = MPReachNLRIAttr_BFN.get_ipv4_unicast_bfn(
    mp_nexthop=tester_agent_ip,
    mp_nlri=["59.66.130.0/24"]
)
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=[], # NLRI is left empty
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_nexthop,
        attr_mpreachnlri
    ] # MP_REACH_NLRI and NEXT_HOP
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_23 = TestCase([open_message, keepalive_message, update_message])

############### testcase 24 ###############

"""
Testcase: UPDATE message with both NLRI, NEXT_HOP and MP_REACH_NLRI attribute.
Same prefix in NLRIs, different next-hop.
(NEXT_HOP before MP_REACH_NLRI, legal next-hop in NEXT_HOP)
"""

# TODO: How does FRR process MP_REACH_NLRI and NEXT_HOP?
# TODO: Does the order matter?

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip)) # Legal next-hop in NEXT_HOP
attr_mpreachnlri = MPReachNLRIAttr_BFN.get_ipv4_unicast_bfn(
    mp_nexthop="10.1.1.1", # Illegal next-hop in MP_REACH_NLRI
    mp_nlri=["59.66.130.0/24"]
)
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.130.0/24"],
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_nexthop,
        attr_mpreachnlri,
    ] # MP_REACH_NLRI and NEXT_HOP
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_24 = TestCase([open_message, keepalive_message, update_message])

############### testcase 25 ###############

"""
Testcase: UPDATE message with both NLRI, NEXT_HOP and MP_REACH_NLRI attribute.
Same prefix in NLRIs, different next-hop. 
(NEXT_HOP before MP_REACH_NLRI, legal next-hop in MP_REACH_NLRI).
"""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN("10.1.1.1")) # Illegal next-hop in NEXT_HOP
attr_mpreachnlri = MPReachNLRIAttr_BFN.get_ipv4_unicast_bfn(
    mp_nexthop=tester_agent_ip, # Legal next-hop in MP_REACH_NLRI
    mp_nlri=["59.66.130.0/24"]
)
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.130.0/24"],
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_nexthop,
        attr_mpreachnlri
    ] # MP_REACH_NLRI and NEXT_HOP
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_25 = TestCase([open_message, keepalive_message, update_message])

############### testcase 26 ###############

"""Testcase: UPDATE message with MP_REACH_NLRI attribute with nontrivial RESERVED field."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_mpreachnlri = MPReachNLRIAttr_BFN.get_ipv4_unicast_bfn(
    mp_nexthop=tester_agent_ip,
    mp_nlri=["59.66.130.0/24"]
)
attr_mpreachnlri.set_reserved_val(b'\x01') # MP_REACH_NLRI with nontrivial RESERVED field
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=[], # NLRI is left empty
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_mpreachnlri
    ]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_26 = TestCase([open_message, keepalive_message, update_message])

############### testcase 27 ###############

"""Testcase: UPDATE message with PathAttrType with nontrivial padding bits."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip))
attr_origin.set_attr_type_lower_bits([1,1,0,1]) # Nontrivial lower bits of the attribute type field
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.130.0/24"],
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_nexthop,
    ]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_27 = TestCase([open_message, keepalive_message, update_message])

############### testcase 28 ###############

"""Testcase: External UPDATE message with LOCAL_PREF attribute."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip))
attr_local_pref = LOCPREFAttr_BFN(LOCPREF_BFN(300))
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.130.0/24"],
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_nexthop,
        attr_local_pref, # Add a LOCAL_PREF attribute
        attr_local_pref,
    ]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_28 = TestCase([open_message, keepalive_message, update_message])

############### testcase 29 ###############

"""Testcase: UPDATE message with nontrivial NLRI padding bits."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip))

nlri_prefix : IPv4Prefix_BFN = IPv4Prefix_BFN.get_bfn("59.66.130.0/20")
nlri_prefix.set_padding_bits([1,0,0,1]) # Set the padding bits of the NLRI prefix

# UPDATE message
update_message_bfn = UpdateMessage_BFN(
    message_content_bfn = UpdateMessageContent_BFN(
        wroutes_len_bfn=Length_BFN(0,2),
        wroutes_bfn=WithdrawnRoutes_BFN([]),
        path_attr_len_bfn=Length_BFN(0,2),
        path_attr_bfn=PathAttributes_BFN(
            [attr_origin, attr_aspath, attr_nexthop]
        ),
        nlri_bfn=NLRI_BFN([nlri_prefix])
    )
)

update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_29 = TestCase([open_message, keepalive_message, update_message])

############### testcase 30 ###############

"""
Testcase: UPDATE message with near-maximum message size (65535).
The size is stuffed by a long COMMUNITIES list. 
Current size is 65533.
"""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# This message now have length 65533
community_list = [(114, op) for op in range(10000,26361)]

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn(
    aspath=[tester_agent_asn],
    next_hop=tester_agent_ip,
    nlri=["59.66.130.0/24"],
    communities=community_list # A very LONG communities list
)

# Show the message size in octets
# print(update_message_bfn.get_binary_length())

update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_30 = TestCase([open_message, keepalive_message, update_message])

############### testcase 31 ###############

"""Testcase: UPDATE message lacking mandatory attribute - NEXT_HOP."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.130.0/24"],
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
    ] # Lacking NEXT_HOP path attribute
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_31 = TestCase([open_message, keepalive_message, update_message])

############### testcase 32 ###############

"""Vanilla testcase: Advertise a route then withdraw."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# UPDATE message 1
update_message_bfn_1 = UpdateMessage_BFN.get_bfn(
    withdrawn_routes=[],
    aspath=[tester_agent_asn],
    next_hop=tester_agent_ip,
    nlri=["59.66.130.0/24"]
)
# UPDATE message 2
update_message_bfn_2 = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=["59.66.130.0/24"],
    nlri=[],
    attr_bfn_list=[]
)
update_message_1 = UpdateMessage(update_message_bfn_1)
update_message_2 = UpdateMessage(update_message_bfn_2)

# testcase
testcase_32 = TestCase(
    [open_message, keepalive_message, update_message_1, Halt(), update_message_2]
)

############### testcase 33 ###############

"""Testcase: Advertise a route then trigger treat-as-withdraw."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# UPDATE message 1
update_message_bfn_1 = UpdateMessage_BFN.get_bfn(
    withdrawn_routes=[],
    aspath=[tester_agent_asn],
    next_hop=tester_agent_ip,
    nlri=["59.66.130.0/24"]
)
# UPDATE message
update_message_bfn_2 = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.130.0/24"],
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
    ] # Lacking NEXT_HOP path attribute, trigger treat-as-withdraw
)
update_message_1 = UpdateMessage(update_message_bfn_1)
update_message_2 = UpdateMessage(update_message_bfn_2)

# testcase
testcase_33 = TestCase(
    [open_message, keepalive_message, update_message_1, Halt(), update_message_2]
)

############### testcase 34 ###############

"""Testcase: Advertise a route with un-discussed path attribute."""

# DIY BGP configuration, leave MP-BGP IPv4 un-used
diy_bgp_config = BGPToolkitConfiguration(
    asn=BGP_CONFIG.asn,
    bgp_identifier=BGP_CONFIG.bgp_identifier,
    hold_time=BGP_CONFIG.hold_time,
    bgp_version=BGP_CONFIG.bgp_version,
    route_refresh=BGP_CONFIG.route_refresh,
    enhanced_route_refresh=BGP_CONFIG.enhanced_route_refresh,
    extended_message=BGP_CONFIG.extended_message,
    graceful_restart=BGP_CONFIG.graceful_restart,
    mpbgp_ipv4_unicast=False
)

# OPEN message
open_message_bfn = OpenMessage_BFN.get_bfn(BGP_CONFIG)
open_message = OpenMessage(open_message_bfn)
# Vanilla KEEPALIVE message
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_mpreachnlri = MPReachNLRIAttr_BFN.get_ipv4_unicast_bfn(
    mp_nexthop=tester_agent_ip,
    mp_nlri=["59.66.130.0/24"]
)
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=[], # NLRI is left empty
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_mpreachnlri
    ] # MP_REACH_NLRI and no NEXT_HOP
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_34 = TestCase([open_message, keepalive_message, update_message])

############### testcase 35 ###############

"""Testcase: UPDATE message with unknown WELL-KNOWN path attribute."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip))
attr_arbitrary = ArbitraryAttr_BFN(
    attr_type_bfn=AttrType_BFN.get_bfn(
        type_code=114, # An unknown type
        higher_bits=[0,1,1,0], # WELL-KNOWN, transitive, partial, no extended length
    ),
    attr_value_bfn=Arbitrary_BFN(value=b'\x11\x45\x14\x19')
) # Unknown path attribute.

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.130.0/24"],
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_nexthop,
        attr_arbitrary,
    ]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_35 = TestCase([open_message, keepalive_message, update_message])

############### testcase 36 ###############

"""Testcase: Withdraw with normal path attributes (No NLRI)."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# UPDATE message 1
update_message_bfn_1 = UpdateMessage_BFN.get_bfn(
    withdrawn_routes=[],
    aspath=[tester_agent_asn],
    next_hop=tester_agent_ip,
    nlri=["59.66.130.0/24"]
)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip))
# UPDATE message 2
update_message_bfn_2 = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=["59.66.130.0/24"],
    nlri=[],
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_nexthop,
    ]
)
update_message_1 = UpdateMessage(update_message_bfn_1)
update_message_2 = UpdateMessage(update_message_bfn_2)

# testcase
testcase_36 = TestCase(
    [open_message, keepalive_message, update_message_1, Halt(), update_message_2]
)

############### testcase 37 ###############

"""Testcase: Withdraw with an unknown OPTIONAL path attribute (No NLRI)."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# UPDATE message 1
update_message_bfn_1 = UpdateMessage_BFN.get_bfn(
    withdrawn_routes=[],
    aspath=[tester_agent_asn],
    next_hop=tester_agent_ip,
    nlri=["59.66.130.0/24"]
)

attr_arbitrary = ArbitraryAttr_BFN(
    attr_type_bfn=AttrType_BFN.get_bfn(
        type_code=114, # An unknown type
        higher_bits=[1,1,1,0], # OPTIONAL, transitive, partial, no extended length
    ),
    attr_value_bfn=Arbitrary_BFN(value=b'\x11\x45\x14\x19')
) # Unknown path attribute.
# UPDATE message 2
update_message_bfn_2 = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=["59.66.130.0/24"],
    nlri=[],
    attr_bfn_list=[
        attr_arbitrary
    ]
)
update_message_1 = UpdateMessage(update_message_bfn_1)
update_message_2 = UpdateMessage(update_message_bfn_2)

# testcase
testcase_37 = TestCase(
    [open_message, keepalive_message, update_message_1, Halt(), update_message_2]
)

############### testcase 38 ###############

"""Testcase: Withdraw with an unknown WELL-KNOWN path attribute (No NLRI)."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# UPDATE message 1
update_message_bfn_1 = UpdateMessage_BFN.get_bfn(
    withdrawn_routes=[],
    aspath=[tester_agent_asn],
    next_hop=tester_agent_ip,
    nlri=["59.66.130.0/24"]
)

attr_arbitrary = ArbitraryAttr_BFN(
    attr_type_bfn=AttrType_BFN.get_bfn(
        type_code=114, # An unknown type
        higher_bits=[0,1,1,0], # WELL-KNOWN, transitive, partial, no extended length
    ),
    attr_value_bfn=Arbitrary_BFN(value=b'\x11\x45\x14\x19')
) # Unknown path attribute.
# UPDATE message 2
update_message_bfn_2 = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=["59.66.130.0/24"],
    nlri=[],
    attr_bfn_list=[
        attr_arbitrary
    ]
)
update_message_1 = UpdateMessage(update_message_bfn_1)
update_message_2 = UpdateMessage(update_message_bfn_2)

# testcase
testcase_38 = TestCase(
    [open_message, keepalive_message, update_message_1, Halt(), update_message_2]
)

############### testcase 39 ###############

"""Testcase: UPDATE message with only an unknown OPTIONAL path attribute (No NLRI)."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_arbitrary = ArbitraryAttr_BFN(
    attr_type_bfn=AttrType_BFN.get_bfn(
        type_code=114, # An unknown type
        higher_bits=[1,1,1,0], # OPTIONAL, transitive, partial, no extended length
    ),
    attr_value_bfn=Arbitrary_BFN(value=b'\x11\x45\x14\x19')
) # Unknown path attribute.
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=[],
    attr_bfn_list=[
        attr_arbitrary
    ]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_39 = TestCase([open_message, keepalive_message, update_message])

############### testcase 40 ###############

"""
Testcase: UPDATE message with both NLRI, NEXT_HOP and MP_REACH_NLRI attribute.
Same prefix in NLRIs, different next-hop.
(NEXT_HOP after MP_REACH_NLRI, legal next-hop in NEXT_HOP)
"""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip)) # Legal next-hop in NEXT_HOP
attr_mpreachnlri = MPReachNLRIAttr_BFN.get_ipv4_unicast_bfn(
    mp_nexthop="10.1.1.1", # Illegal next-hop in MP_REACH_NLRI
    mp_nlri=["59.66.130.0/24"]
)
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.130.0/24"],
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_mpreachnlri,
        attr_nexthop,
    ] # MP_REACH_NLRI and NEXT_HOP
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_40 = TestCase([open_message, keepalive_message, update_message])

############### testcase 41 ###############

"""
Testcase: UPDATE message with both NLRI, NEXT_HOP and MP_REACH_NLRI attribute.
Same prefix in NLRIs, different next-hop. 
(NEXT_HOP after MP_REACH_NLRI, legal next-hop in MP_REACH_NLRI).
"""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN("10.1.1.1")) # Illegal next-hop in NEXT_HOP
attr_mpreachnlri = MPReachNLRIAttr_BFN.get_ipv4_unicast_bfn(
    mp_nexthop=tester_agent_ip, # Legal next-hop in MP_REACH_NLRI
    mp_nlri=["59.66.130.0/24"]
)
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.130.0/24"],
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_mpreachnlri,
        attr_nexthop,
    ] # MP_REACH_NLRI and NEXT_HOP
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_41 = TestCase([open_message, keepalive_message, update_message])

############### testcase 42 ###############

"""
Testcase: UPDATE message with both NEXT_HOP and MP_REACH_NLRI attribute.
Same prefix in NLRIs, different next-hop. 
(legal next-hop in NEXT_HOP).
"""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip)) # Legal next-hop in NEXT_HOP
attr_mpreachnlri = MPReachNLRIAttr_BFN.get_ipv4_unicast_bfn(
    mp_nexthop="10.1.1.1", # Illegal next-hop in MP_REACH_NLRI
    mp_nlri=["59.66.130.0/24"]
)
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=[], # No NLRI
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_mpreachnlri,
        attr_nexthop,
    ] # MP_REACH_NLRI and NEXT_HOP
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_42 = TestCase([open_message, keepalive_message, update_message])

############### testcase 43 ###############

"""
Testcase: UPDATE message with both NEXT_HOP and MP_REACH_NLRI attribute.
Same prefix in NLRIs, different next-hop. 
(legal next-hop in MP_REACH_NLRI).
"""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN("10.1.1.1")) # Illegal next-hop in NEXT_HOP
attr_mpreachnlri = MPReachNLRIAttr_BFN.get_ipv4_unicast_bfn(
    mp_nexthop=tester_agent_ip, # Legal next-hop in MP_REACH_NLRI
    mp_nlri=["59.66.130.0/24"]
)
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=[], # No NLRI
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_mpreachnlri,
        attr_nexthop,
    ] # MP_REACH_NLRI and NEXT_HOP
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_43 = TestCase([open_message, keepalive_message, update_message])

############### testcase 44 ###############

"""Testcase: UPDATE message with MP_REACH_NLRI attribute with illegal NEXT_HOP value."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_mpreachnlri = MPReachNLRIAttr_BFN.get_ipv4_unicast_bfn(
    mp_nexthop="10.1.1.1", # illegal NEXT_HOP value
    mp_nlri=["59.66.130.0/24"]
)
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=[], # NLRI is left empty
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_mpreachnlri
    ] # MP_REACH_NLRI and no NEXT_HOP
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_44 = TestCase([open_message, keepalive_message, update_message])

############### testcase 45 ###############

"""
Testcase: UPDATE message with unknown path attribute.
AND there is another path attribute embedded in the path attribute.
"""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip))
attr_arbitrary = ArbitraryAttr_BFN(
    attr_type_bfn=AttrType_BFN.get_bfn(
        type_code=114, # An unknown type
        higher_bits=[1,1,1,0], # optional, transitive, partial, no extended length
    ),
    # Embed a NEXT_HOP attribute in the path attribute.
    attr_value_bfn=Arbitrary_BFN(value=attr_nexthop.get_binary_expression())
) # Unknown path attribute.

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.130.0/24"],
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_nexthop,
        attr_arbitrary,
    ]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_45 = TestCase([open_message, keepalive_message, update_message])

############### testcase 46 ###############

"""
Testcase: WELL-KNOWN attribute not transitive.
"""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip))
attr_nexthop.set_is_transitive(False) # WELL-KNOWN attribute not transitive!
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.130.0/24"],
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_nexthop,
    ]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_46 = TestCase([open_message, keepalive_message, update_message])

############### testcase 47 ###############

"""Testcase: UPDATE message with only an incomplete Marker field."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# UPDATE message with only an incomplete Marker field
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_bval(b"\xff"*7)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_47 = TestCase([open_message, keepalive_message, update_message])

############### testcase 48 ###############

"""Testcase: UPDATE message with a large length and no content."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# UPDATE message with only an incomplete Marker field
update_message_bfn = UpdateMessage_BFN.get_empty_message_bfn()
update_message_bfn.set_length(24) # Set a large length
update_message_bfn.set_message_content_bval(b"") # and set the message content into empty value
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_48 = TestCase([open_message, keepalive_message, update_message])

############### testcase 49 ###############

"""
BGP Update with the overall attribute field length exceeding the message length.
"""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn(
    withdrawn_routes=[],
    aspath=[tester_agent_asn],
    next_hop=tester_agent_ip,
    nlri=["59.66.130.0/24"]
)
update_message_bfn.set_path_attr_len(200) # overall attribute length exceeding the message length.
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_49 = TestCase([open_message, keepalive_message, update_message])

############### testcase 50 ###############

"""
Testcase: UPDATE message with one particular attribute field length exceeding the message length.
"""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip))
attr_aspath.set_length(200) # an attribute length exceeding the message length.
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.130.0/24"],
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_nexthop,
    ]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_50 = TestCase([open_message, keepalive_message, update_message])

############### testcase 51 ###############

"""
Testcase: WELL-KNOWN attribute with partial bit 1: ORIGIN
Violating RFC 4271: "For well-known attributes and for optional non-transitive attributes, the Partial bit MUST be set to 0."
"""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip))
attr_origin.set_is_partial(True) # WELL-KNOWN attribute with partial bit 1!
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.130.0/24"],
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_nexthop,
    ]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_51 = TestCase([open_message, keepalive_message, update_message])

############### testcase 52 ###############

"""
Testcase: WELL-KNOWN attribute with partial bit 1: AS_PATH
Violating RFC 4271: "For well-known attributes and for optional non-transitive attributes, the Partial bit MUST be set to 0."
"""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip))
attr_aspath.set_is_partial(True) # WELL-KNOWN attribute with partial bit 1!
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.130.0/24"],
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_nexthop,
    ]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_52 = TestCase([open_message, keepalive_message, update_message])

############### testcase 53 ###############

"""
Testcase: WELL-KNOWN attribute with partial bit 1: NEXT_HOP
Violating RFC 4271: "For well-known attributes and for optional non-transitive attributes, the Partial bit MUST be set to 0."
"""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip))
attr_nexthop.set_is_partial(True) # WELL-KNOWN attribute with partial bit 1!
# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.130.0/24"],
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_nexthop,
    ]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_53 = TestCase([open_message, keepalive_message, update_message])

############### testcase 54 ###############

"""
Testcase: UPDATE message with near-maximum message size (65535).
The size is stuffed by an unknown optional transitive attribute. 
Current size is 65534.
"""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip))
attr_arbitrary = ArbitraryAttr_BFN(
    attr_type_bfn=AttrType_BFN.get_bfn(
        type_code=114, # An unknown type,
        higher_bits=[1,1,1,1], # optional, transitive, partial, use extended length
    ),
    attr_value_bfn=Arbitrary_BFN(value=b'\x00'*65485)
) # Unknown path attribute.

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.130.0/24"],
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_nexthop,
        attr_arbitrary,
    ]
)
update_message = UpdateMessage(update_message_bfn)

# Show the message size in octets
# print(update_message_bfn.get_binary_length())

# testcase
testcase_54 = TestCase([open_message, keepalive_message, update_message])

############### testcase 55 ###############

"""
Testcase: UPDATE message with some random contents attached to the end.
"""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn(
    withdrawn_routes=[],
    aspath=[tester_agent_asn],
    next_hop=tester_agent_ip,
    nlri=["59.66.130.0/24"]
)
update_message_bfn.set_bval(update_message_bfn.get_binary_expression()+b"\x01"*5)
# update_message_bfn.set_bval(update_message_bfn.get_binary_expression()+update_message_bfn.get_binary_expression())
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_55 = TestCase([open_message, keepalive_message, update_message])

############### testcase 56 ###############

"""Testcase: UPDATE message with repeated unknown path attribute."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip))
attr_arbitrary = ArbitraryAttr_BFN(
    attr_type_bfn=AttrType_BFN.get_bfn(
        type_code=114, # An unknown type
        higher_bits=[1,1,1,0], # optional, transitive, partial, no extended length
    ),
    attr_value_bfn=Arbitrary_BFN(value=b'\x11\x45\x14\x19')
) # Unknown path attribute.

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
    withdrawn_routes=[],
    nlri=["59.66.130.0/24"],
    attr_bfn_list=[
        attr_origin,
        attr_aspath,
        attr_nexthop,
        attr_arbitrary,
        attr_arbitrary, # Repeated unknown path attribute.
    ]
)
update_message = UpdateMessage(update_message_bfn)

# testcase
testcase_56 = TestCase([open_message, keepalive_message, update_message])

##############################################
#               Testcase Suite               #
##############################################

single_testcase_suite = [
    testcase_0, 
    testcase_1,
    testcase_2,
    testcase_3,
    testcase_4,
    testcase_5,
    testcase_6,
    testcase_7,
    testcase_8,
    testcase_9,
    testcase_10,
    testcase_11,
    testcase_12,
    testcase_13,
    testcase_14,
    testcase_15,
    testcase_16,
    testcase_17,
    testcase_18,
    testcase_19,
    testcase_20,
    testcase_21,
    testcase_22,
    testcase_23,
    testcase_24,
    testcase_25,
    testcase_26,
    testcase_27,
    testcase_28,
    testcase_29,
    testcase_30,
    testcase_31,
    testcase_32,
    testcase_33,
    testcase_34,
    testcase_35,
    testcase_36,
    testcase_37,
    testcase_38,
    testcase_39,
    testcase_40,
    testcase_41,
    testcase_42,
    testcase_43,
    testcase_44,
    testcase_45,
    testcase_46,
    testcase_47,
    testcase_48,
    testcase_49,
    testcase_50,
    testcase_51,
    testcase_52,
    testcase_53,
    testcase_54,
    testcase_55,
    testcase_56,
]
