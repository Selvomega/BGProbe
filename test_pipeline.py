import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_agent.test_agent import TestAgent
from test_agent.test_suite import TestCase, TestSuite
from _obsoleted_bgp_utils.msg_base import Message
from _obsoleted_bgp_utils.msg_open import OpenMessage
from _obsoleted_bgp_utils.msg_keepalive import KeepAliveMessage
from _obsoleted_bgp_utils.bgp_client_configuration import BGPClientConfiguration
from _obsoleted_bgp_utils.basic_types import IP, IPPrefix
from _obsoleted_bgp_utils.open_opt import OptionalParameters
from network_utils.tcp_client import TCPClientConfiguration
from routing_software_interface.basic_types import RouterConfiguration, RouterSoftwareType, Neighbor

from vnet_config import VNET_CONFIG

router = VNET_CONFIG["router_software"]
client = VNET_CONFIG["clients"][0]

router_asn = 65001
client_asn = 65002

client_bgp_identifier = IP(client["ip"])
client_ip = IP(client["ip"])
client_namespace = client["namespace"]

open_message_content = OpenMessage(
    asn=client_asn,
    bgp_identifier=client_bgp_identifier,
    optional_parameters=OptionalParameters([])
)
keepalive_message_content = KeepAliveMessage()

open_message = Message(message_content=open_message_content)
keepalive_message = Message(keepalive_message_content)

testcase0 = TestCase([open_message])
testcase1 = TestCase([open_message,keepalive_message])
testcase2 = TestCase([open_message,keepalive_message])

test_suite = TestSuite([testcase1])

def temp_func():
    """Boo..."""
    return False

bgp_client_config = BGPClientConfiguration(client_asn, client_ip)
tcp_client_config = TCPClientConfiguration(host=IP(router["ip"]).get_str_expression(),
                                           port=179,
                                           bind_val=(client_ip.get_str_expression(), 0),
                                           netns=client_namespace)
router_config = RouterConfiguration(
    asn=router_asn,
    router_id=IP(router["ip"]),
    neighbors=[Neighbor(
        peer_ip=client_ip,
        peer_asn=client_asn,
        local_source=router["veth"]
    )],
    # local_prefixes=[
    #     IPPrefix('192.0.2.0/24')
    # ]
)

test_agent = TestAgent(
    bgp_client_config = bgp_client_config,
    tcp_client_config = tcp_client_config,
    router_config = router_config,
    router_type=RouterSoftwareType.FRR,
    test_suite=test_suite,
    check_func=temp_func,
    dump_path="temp.pkl"
)

test_agent.run_test_suite()
