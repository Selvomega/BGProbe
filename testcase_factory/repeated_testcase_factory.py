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
from basic_utils.file_utils import *
from basic_utils.const import *
from basic_utils.serialize_utils import *

from .basic_types import TestCase, Halt

from bgprobe_config import *
from .single_testcase_factory import single_testcase_suite

############### Vanilla messages ###############

# Vanilla OPEN message
open_message_bfn = OpenMessage_BFN.get_bfn(BGP_CONFIG)
vanilla_open_message = OpenMessage(open_message_bfn)

# Vanilla KEEPALIVE message
keepalive_message_bfn = KeepAliveMessage_BFN.get_bfn()
vanilla_keepalive_message = KeepAliveMessage(keepalive_message_bfn)

# Vanilla UPDATE message
update_message_bfn = UpdateMessage_BFN.get_empty_message_bfn()
vanilla_update_message = UpdateMessage(update_message_bfn)

############### testcase 0 ###############

"""
Vanilla testcase.
"""

testcase_0 = TestCase([vanilla_open_message,
                       vanilla_keepalive_message,
                       vanilla_update_message])
testcase_name_0 = "vanilla_testcase"

############### testcase 0 ###############

repeated_testcase_suite = [
    (testcase_0, testcase_name_0),
]
