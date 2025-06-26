# This file is used to test the BGP routing software in a decomposed manner.
# You have to set up the BGP daemon and observe the log manually (and out of this script).
# The routing software is NOT automatically set-up and torn-down, only TCP client is auto-managed.

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from time import sleep
from bgp_toolkit.message import OpenMessage_BFN, OpenMessage, KeepAliveMessage_BFN, KeepAliveMessage, UpdateMessage_BFN, UpdateMessage

from network_utils.tcp_client import TCPClientConfiguration, TCPClient
from routing_software_interface.basic_types import RouterConfiguration, RouterSoftwareType, Neighbor
from routing_software_interface.utils import get_router_interface
from basic_utils.binary_utils import make_bytes_displayable

from testcase_factory.single_testcase_factory import VNET_CONFIG, BGP_CONFIG
from testcase_factory.single_testcase_factory import testcase_1, testcase_2
from testcase_factory.basic_types import TestCase, Halt

from testbed import *

########## Local network configuration ##########

# BGP software configuration
router_software = VNET_CONFIG["router_software"]
# Software tester configuration
client = VNET_CONFIG["clients"][0]

########## NO USE: hint the manual configuration of the routing software. ##########

router_software_asn = 65001
client_asn = 65002
client_bgp_identifier = client["ip"].split('/')[0] # BGP identifier

########## Configure the TCP client ##########

client_ip = client["ip"].split('/')[0] # IP address
router_software_ip = router_software["ip"].split('/')[0] # IP address 
client_namespace = client["namespace"] # Local network namespace used 

# Configure the TCP client used for the TestAgent
tcp_client_config = TCPClientConfiguration(host=router_software_ip,
                                           port=179,
                                           bind_val=(client_ip, 0),
                                           netns=client_namespace)

########## Configure the router software (2) ##########

# Select the testcase
testcase = testcase_2

# Run the testcase
tcp_client = TCPClient(tcp_client_config)
tcp_client.start()
print("here")
for message in testcase:
    print("MMMM")
    tcp_client.send(message.get_binary_expression())
    print("EEEE")
    sleep(0.5)
sleep(40)
tcp_client.end()
