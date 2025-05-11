# DIY testcases here!

from copy import deepcopy
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bgp_utils.message import OpenMessage_BFN, OpenMessage, KeepAliveMessage_BFN, KeepAliveMessage, UpdateMessageContent_BFN, UpdateMessage_BFN, UpdateMessage, WithdrawnRoutes_BFN, NLRI_BFN, PathAttributes_BFN
from bgp_utils.path_attribute import AttrType_BFN, BaseAttr_BFN, OriginType, Origin_BFN, OriginAttr_BFN, PathSegementType, PathSegmentType_BFN, PathSegmentLength_BFN, PathSegmentValue_BFN, PathSegment_BFN, ASPath_BFN, ASPathAttr_BFN, NextHop_BFN, NextHopAttr_BFN, Communities_BFN, CommunitiesAttr_BFN, MPReachNLRI_BFN, MPReachNLRIAttr_BFN, MPUnreachNLRI_BFN, MPUnreachNLRIAttr_BFN, LOCPREF_BFN, LOCPREFAttr_BFN, Arbitrary_BFN, ArbitraryAttr_BFN
from bgp_utils.basic_bfn_types import IPv4Prefix_BFN, Length_BFN
from basic_utils.binary_utils import bytes2num
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

"""Vanilla testcase: Trivial UPDATE message."""

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

"""Testcase: Unmatched next-hop."""
# This is expected to be ignored but not hurt the connection

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

"""Testcase: Unmatched last AS number."""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn(
    withdrawn_routes=[],
    aspath=[1145, tester_client_asn], # Unmatched AS number
    next_hop=tester_client_ip,
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

attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_client_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_client_ip))
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
    aspath=[tester_client_asn],
    next_hop=tester_client_ip,
    nlri=["59.66.130.0/24"] # NO NLRI attribute.
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
    aspath=[tester_client_asn],
    next_hop=tester_client_ip,
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
    aspath=([tester_client_asn,114],[514,1919,810]),
    next_hop=tester_client_ip,
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
    aspath=[tester_client_asn,114,514,1919,114],
    next_hop=tester_client_ip,
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
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_client_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_client_ip))
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
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_client_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_client_ip))
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
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_client_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_client_ip))
attr_communities = CommunitiesAttr_BFN.get_bfn(
    [(router_software_asn, 114)]
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
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_client_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_client_ip))
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
attr_aspath_1 = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_client_asn, 114]))
attr_aspath_2 = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_client_asn, 514]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_client_ip))

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
    ASPath_BFN.get_bfn(as_path=[tester_client_asn] + [i for i in range(64000,64254)]),
    ext_len=True
) # AS_PATH with near-maximum length (one more to make the AS segment overflow).
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_client_ip))

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
    aspath=[tester_client_asn],
    next_hop=tester_client_ip,
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
    aspath=[tester_client_asn],
    next_hop=tester_client_ip,
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
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_client_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_client_ip))
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
    aspath=[tester_client_asn],
    next_hop=tester_client_ip,
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
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_client_asn]))
attr_mpreachnlri = MPReachNLRIAttr_BFN.get_ipv4_unicast_bfn(
    mp_nexthop=tester_client_ip,
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
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_client_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_client_ip))
attr_mpreachnlri = MPReachNLRIAttr_BFN.get_ipv4_unicast_bfn(
    mp_nexthop=tester_client_ip,
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
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_client_asn]))
attr_mpreachnlri_0 = MPReachNLRIAttr_BFN.get_ipv4_unicast_bfn(
    mp_nexthop=tester_client_ip,
    mp_nlri=["59.66.130.0/24"]
)
attr_mpreachnlri_1 = MPReachNLRIAttr_BFN.get_ipv4_unicast_bfn(
    mp_nexthop=tester_client_ip,
    mp_nlri=["59.66.131.0/24"]
)
attr_mpreachnlri_2 = MPReachNLRIAttr_BFN.get_ipv4_unicast_bfn(
    mp_nexthop=tester_client_ip,
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
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_client_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_client_ip))
attr_mpreachnlri = MPReachNLRIAttr_BFN.get_ipv4_unicast_bfn(
    mp_nexthop=tester_client_ip,
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
Same prefix in NLRIs, different next-hop (Legal next-hop in NEXT_HOP)
"""

# TODO: How does FRR process MP_REACH_NLRI and NEXT_HOP?
# TODO: Does the order matter?

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_client_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_client_ip)) # Legal next-hop in NEXT_HOP
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
Same prefix in NLRIs, different next-hop (Legal next-hop in MP_REACH_NLRI)
"""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_client_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN("10.1.1.1")) # Illegal next-hop in NEXT_HOP
attr_mpreachnlri = MPReachNLRIAttr_BFN.get_ipv4_unicast_bfn(
    mp_nexthop=tester_client_ip, # Legal next-hop in MP_REACH_NLRI
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
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_client_asn]))
attr_mpreachnlri = MPReachNLRIAttr_BFN.get_ipv4_unicast_bfn(
    mp_nexthop=tester_client_ip,
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
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_client_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_client_ip))
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
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_client_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_client_ip))
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
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_client_asn]))
attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_client_ip))

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
Current size is 65533.
"""

# Vanilla OPEN and KEEPALIVE message
open_message = deepcopy(vanilla_open_message)
keepalive_message = deepcopy(vanilla_keepalive_message)

# This message now have length 65533
community_list = [(114, op) for op in range(10000,26361)]

# UPDATE message
update_message_bfn = UpdateMessage_BFN.get_bfn(
    aspath=[tester_client_asn],
    next_hop=tester_client_ip,
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
attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_client_asn]))
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






##############################################
#               Testcase Suite               #
##############################################

testcase_suite = [
    None, 
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
]
