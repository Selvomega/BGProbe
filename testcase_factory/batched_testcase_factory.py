# DIY test batch here!

from copy import deepcopy
import sys, os, subprocess, random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from basic_utils.time_utils import get_current_time
from basic_utils.file_utils import *
from basic_utils.const import *
from basic_utils.serialize_utils import *

from bgp_toolkit.message import OpenMessage_BFN, OpenMessage, KeepAliveMessage_BFN, KeepAliveMessage, UpdateMessageContent_BFN, UpdateMessage_BFN, UpdateMessage, WithdrawnRoutes_BFN, NLRI_BFN, PathAttributes_BFN
from bgp_toolkit.path_attribute import AttrType_BFN, BaseAttr_BFN, OriginType, Origin_BFN, OriginAttr_BFN, PathSegementType, PathSegmentType_BFN, PathSegmentLength_BFN, PathSegmentValue_BFN, PathSegment_BFN, ASPath_BFN, ASPathAttr_BFN, NextHop_BFN, NextHopAttr_BFN, Communities_BFN, CommunitiesAttr_BFN, MPReachNLRI_BFN, MPReachNLRIAttr_BFN, MPUnreachNLRI_BFN, MPUnreachNLRIAttr_BFN, LOCPREF_BFN, LOCPREFAttr_BFN, Arbitrary_BFN, ArbitraryAttr_BFN
from bgp_toolkit.basic_bfn_types import IPv4Prefix_BFN, Length_BFN
from bgp_toolkit.binary_field_node import BinaryFieldNode

from testcase_factory.basic_types import TestCase, Halt

from bgprobe_config import *

TEST_BATCH_DIR = f"{REPO_ROOT_PATH}/testcase_factory/batched_testcases"

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

############### Vanilla path attributes ###############

vanilla_attr_origin = OriginAttr_BFN(Origin_BFN(OriginType.IGP))
vanilla_attr_aspath = ASPathAttr_BFN(ASPath_BFN.get_bfn(as_path=[tester_agent_asn]))
vanilla_attr_nexthop = NextHopAttr_BFN(NextHop_BFN(tester_agent_ip))

############### Define some constant prefixes ###############

CONST_PREFIX = "59.66.130.0/24"

############### the general function used to generate test batches ###############

def generate_test_batch(gen_func,
                        testcase_num: int,
                        test_batch_name: str,
                        include_timestamp: bool = False):
    """
    Generate the test batch from the generating function and the test batch name.
    """
    if include_timestamp:
        test_batch_name = f"{test_batch_name}_{get_current_time()}"
    target_file =  f"{TEST_BATCH_DIR}/{test_batch_name}.pkl"
    if file_exists(target_file):
        delete_file(target_file)
    testcase_list = []
    for _ in range(0, testcase_num):
        testcase = gen_func()
        testcase_list.append(testcase)
    save_variable_to_file(testcase_list,target_file)

############### Test bacth generating functions ###############

def vanilla_gen() -> TestCase:
    """
    Generate trivial UPDATE messages.
    """
    # UPDATE message
    update_message_bfn = UpdateMessage_BFN.get_bfn_diy_attr(
        withdrawn_routes=[],
        nlri=[CONST_PREFIX],
        attr_bfn_list=[
            vanilla_attr_origin,
            vanilla_attr_aspath,
            vanilla_attr_nexthop,
        ]
    )
    update_message = UpdateMessage(update_message_bfn)

    return TestCase([vanilla_open_message, vanilla_keepalive_message, update_message])

def random_unknown_attribute() -> TestCase:
    """
    Generate UPDATE messages with a random unknown attribute.
    """
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
            vanilla_attr_origin,
            vanilla_attr_aspath,
            vanilla_attr_nexthop,
            attr_arbitrary,
        ]
    )
    update_message = UpdateMessage(update_message_bfn)

    return TestCase([vanilla_open_message, vanilla_keepalive_message, update_message])

def random_descendent_bfn():
    """
    Randomly mutate one BFN under the UPDATE message
    """
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
        nlri=[CONST_PREFIX],
        attr_bfn_list=[
            attr_nexthop,
            attr_origin,
            attr_aspath,
            attr_arbitrary
        ] # Out-of-order path attributes
    )
    update_message_bfn.sample_under_cone(
        BinaryFieldNode.is_bfn
    ).uniformly_apply_mutation()
    update_message = UpdateMessage(update_message_bfn)

    return TestCase([vanilla_open_message, vanilla_keepalive_message, update_message])

def random_length_bfn():
    """
    Randomly mutate one Length_BFN under the UPDATE message by modifying its value randomly.
    """
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
        nlri=[CONST_PREFIX],
        attr_bfn_list=[
            attr_nexthop,
            attr_origin,
            attr_aspath,
            attr_arbitrary
        ] # Out-of-order path attributes
    )
    to_be_mutated : Length_BFN = update_message_bfn.sample_under_cone(
        BinaryFieldNode.is_length_bfn
    )

    # Set the length value to 0 with probability 0.1
    rand_len_val = 0 if probability_true(0.1) else to_be_mutated.random_length()
    to_be_mutated.set_length(rand_len_val)

    update_message = UpdateMessage(update_message_bfn)

    return TestCase([vanilla_open_message, vanilla_keepalive_message, update_message])

def random_attribute_bfn():
    """
    Randomly mutate one attribute BFN under the UPDATE message.
    """
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
        nlri=[CONST_PREFIX],
        attr_bfn_list=[
            attr_nexthop,
            attr_origin,
            attr_aspath,
            attr_arbitrary
        ] # Out-of-order path attributes
    )
    # Sample an attribute to be mutated
    sampled_attr = update_message_bfn.sample_under_cone(
        BinaryFieldNode.is_attr_bfn
    )
    # print(sampled_attr.get_bfn_name())
    # Randomly mutate one field in the attribute.
    sampled_attr.sample_under_cone(
        BinaryFieldNode.is_bfn
    ).uniformly_apply_mutation()

    update_message = UpdateMessage(update_message_bfn)

    return TestCase([vanilla_open_message, vanilla_keepalive_message, update_message])

if __name__ == "__main__":
    """
    Generate the test batch
    """

    gen_func = random_unknown_attribute
    testcase_num = 1024
    test_batch_name = "random_unknown_attribute"
    include_timestamp = False

    generate_test_batch(
        gen_func=gen_func,
        testcase_num=testcase_num,
        test_batch_name=test_batch_name,
        include_timestamp=include_timestamp
    )
