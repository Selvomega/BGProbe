import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_agent.test_agent import TestAgent
from test_agent.test_suite import TestCase, TestSuite
from bgp_utils.msg_base import Message
from bgp_utils.msg_open import OpenMessage
from bgp_utils.msg_keepalive import KeepAliveMessage
from bgp_utils.bgp_client_configuration import BGPClientConfiguration
from bgp_utils.basic_types import IP
from bgp_utils.open_opt import OptionalParameters
from network_utils.tcp_client import TCPClientConfiguration
from routing_software_interface.basic_types import RouterConfiguration, RouterSoftwareType

asn = 65002
bgp_identifier = IP('2.2.2.2')
bgp_client_ip = IP('127.0.0.2')

open_message_content = OpenMessage(
    asn=asn,
    bgp_identifier=bgp_identifier,
    optional_parameters=OptionalParameters([])
)
keepalive_message_content = KeepAliveMessage()

open_message = Message(message_content=open_message_content)
keepalive_message = Message(keepalive_message_content)

testcase0 = TestCase([open_message])
testcase1 = TestCase([open_message,keepalive_message])
testcase2 = TestCase([open_message,keepalive_message])

test_suite = TestSuite([testcase0])

def temp_func():
    """Boo..."""
    return True

bgp_client_config = BGPClientConfiguration(asn, bgp_client_ip)
tcp_client_config = TCPClientConfiguration(host='127.0.0.1',port=179,bind_val=('127.0.0.2', 0))
print(tcp_client_config)
router_config = RouterConfiguration(
    asn=65001,
    router_id=IP('1.1.1.1')
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
