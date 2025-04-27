import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bgp_utils.message import OpenMessage_BFN, OpenMessage, KeepAliveMessage_BFN, KeepAliveMessage, UpdateMessage_BFN, UpdateMessage
from bgp_utils.bgp_configuration import BGP_Configuration, parse_bgp_config_from_yaml
from test_agent.test_agent import TestAgent
from test_agent.test_suite import TestCase, TestSuite
from network_utils.tcp_client import TCPClientConfiguration
from routing_software_interface.basic_types import RouterConfiguration, RouterSoftwareType, Neighbor
from basic_utils.binary_utils import make_bytes_displayable

from testcase_factory import VNET_CONFIG, BGP_CONFIG
from testcase_factory import testcase_1, testcase_2

########## Local network configuration ##########

# BGP software configuration
router_software = VNET_CONFIG["router_software"]
# Software tester configuration
client = VNET_CONFIG["clients"][0]

########## Configure the router software (1) ##########

router_software_asn = 65001 # AS number 
router_software_ip = router_software["ip"].split('/')[0] # IP address 

########## Configure the client ##########

client_namespace = client["namespace"] # Local network namespace used 
client_asn = BGP_CONFIG.asn # AS number 
client_bgp_identifier = client["ip"].split('/')[0] # BGP identifier
client_ip = client["ip"].split('/')[0] # IP address

# Configure the TCP client used for the TestAgent
tcp_client_config = TCPClientConfiguration(host=router_software_ip,
                                           port=179,
                                           bind_val=(client_ip, 0),
                                           netns=client_namespace)

########## Configure the router software (2) ##########

router_config = RouterConfiguration(
    asn=router_software_asn,
    router_id=router_software_ip,
    neighbors=[Neighbor(
        peer_ip=client_ip,
        peer_asn=client_asn,
        local_source=router_software["veth"]
    )],
)

########## Initialize the TestAgent ##########

test_agent = TestAgent(
    tcp_client_config = tcp_client_config,
)

########## Run testcase ##########

test_agent.run_single_testcase(
    test_case=testcase_1,
    router_configuration=router_config,
)
