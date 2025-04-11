import sys
import os
from time import sleep
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_agent.test_agent import TestAgent
from test_agent.test_suite import TestCase, TestSuite
from bgp_utils.msg_base import Message
from bgp_utils.msg_open import OpenMessage
from bgp_utils.msg_keepalive import KeepAliveMessage
from bgp_utils.bgp_client_configuration import BGPClientConfiguration
from bgp_utils.basic_types import IP
from bgp_utils.open_opt import OptionalParameters
from network_utils.tcp_client import TCPClientConfiguration, TCPClient
from routing_software_interface.basic_types import RouterConfiguration, RouterSoftwareType

client_config = TCPClientConfiguration(
    '127.0.0.1',
    179,
    ('127.0.0.2',0)
)

client = TCPClient(client_config)
client.start()
sleep(10)
