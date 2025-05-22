# DIY testcases here!

from copy import deepcopy
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bgp_utils.message import OpenMessage_BFN, OpenMessage, KeepAliveMessage_BFN, KeepAliveMessage, UpdateMessageContent_BFN, UpdateMessage_BFN, UpdateMessage, WithdrawnRoutes_BFN, NLRI_BFN, PathAttributes_BFN
from bgp_utils.path_attribute import AttrType_BFN, BaseAttr_BFN, OriginType, Origin_BFN, OriginAttr_BFN, PathSegementType, PathSegmentType_BFN, PathSegmentLength_BFN, PathSegmentValue_BFN, PathSegment_BFN, ASPath_BFN, ASPathAttr_BFN, NextHop_BFN, NextHopAttr_BFN, Communities_BFN, CommunitiesAttr_BFN, MPReachNLRI_BFN, MPReachNLRIAttr_BFN, MPUnreachNLRI_BFN, MPUnreachNLRIAttr_BFN, LOCPREF_BFN, LOCPREFAttr_BFN, Arbitrary_BFN, ArbitraryAttr_BFN
from bgp_utils.basic_bfn_types import IPv4Prefix_BFN, Length_BFN
from bgp_utils.binary_field_node import *
from basic_utils.binary_utils import bytes2num, make_bytes_displayable
from basic_utils.file_utils import *
from basic_utils.const import *
from basic_utils.serialize_utils import *
from test_agent.test_suite import TestCase, Halt

from test_configuration import *
from .single_testcase_factory import single_testcase_suite

############### Vanilla messages ###############

# Vanilla OPEN message
open_message_bfn = OpenMessage_BFN.get_bfn(BGP_CONFIG)
vanilla_open_message = OpenMessage(open_message_bfn)

# Vanilla KEEPALIVE message
keepalive_message_bfn = KeepAliveMessage_BFN.get_bfn()
vanilla_keepalive_message = KeepAliveMessage(keepalive_message_bfn)

############### testcase 0 ###############

"""
The testcase 3 of random_attribute_bfn test batch may cause software crash.
"""

data_file_path = f"{REPO_ROOT_PATH}/test_batches/random_attribute_bfn.pkl"
testcase_0 = read_variables_from_file(data_file_path)[0][2]
testcase_name_0 = "random_attribute_bfn_testcase_3"

############### testcase 0 ###############

"""
The testcase 22 of random_attribute_bfn test batch may cause software crash.
"""

data_file_path = f"{REPO_ROOT_PATH}/test_batches/random_attribute_bfn.pkl"
testcase_1 = read_variables_from_file(data_file_path)[0][21]
testcase_name_1 = "random_attribute_bfn_testcase_22"

repeated_testcase_suite = [
    (testcase_0, testcase_name_0),
    (testcase_1, testcase_name_1),
]
