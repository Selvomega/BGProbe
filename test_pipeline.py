import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bgp_utils.message import OpenMessage_BFN, OpenMessage, KeepAliveMessage_BFN, KeepAliveMessage
from bgp_utils.bgp_configuration import BGP_Configuration, parse_bgp_config_from_yaml
from test_agent.test_agent import TestAgent
from test_agent.test_suite import TestCase, TestSuite
from network_utils.tcp_client import TCPClientConfiguration
from routing_software_interface.basic_types import RouterConfiguration, RouterSoftwareType, Neighbor
from basic_utils.binary_utils import make_bytes_displayable

from vnet_config import VNET_CONFIG

BGP_CONFIG : BGP_Configuration = parse_bgp_config_from_yaml("bgp_config.yaml")

router = VNET_CONFIG["router_software"]
client = VNET_CONFIG["clients"][0]

router_asn = 65001
client_asn = 65002

client_bgp_identifier = client["ip"].split('/')[0]
client_ip = client["ip"].split('/')[0]
router_ip = router["ip"].split('/')[0]
client_namespace = client["namespace"]

open_message_bfn = OpenMessage_BFN.get_bfn(BGP_CONFIG)

keepalive_message_bfn = KeepAliveMessage_BFN.get_bfn()

open_message = OpenMessage(open_message_bfn)
print(make_bytes_displayable(open_message.get_binary_expression()))
keepalive_message = KeepAliveMessage(keepalive_message_bfn)

testcase0 = TestCase([open_message])
testcase1 = TestCase([open_message,keepalive_message])

def temp_func():
    """Boo..."""
    return False

tcp_client_config = TCPClientConfiguration(host=router_ip,
                                           port=179,
                                           bind_val=(client_ip, 0),
                                           netns=client_namespace)
router_config = RouterConfiguration(
    asn=router_asn,
    router_id=router_ip,
    neighbors=[Neighbor(
        peer_ip=client_ip,
        peer_asn=client_asn,
        local_source=router["veth"]
    )],
)

test_agent = TestAgent(
    tcp_client_config = tcp_client_config,
)

test_agent.run_single_testcase(
    test_case=testcase1,
    router_configuration=router_config,
)
