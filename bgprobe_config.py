# This file defines the variables used to configure the test.

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bgp_toolkit.bgp_toolkit_configuration import BGPToolkitConfiguration, parse_bgp_config_from_yaml
from test_agents.exabgp_agent import generate_exabgp_config, ExaBGPAgentConfiguration
from test_agents.tcp_agent import TCPAgentConfiguration
from test_agents.router_agent import RouterAgentType
from network_utils.utils import get_ipv4_prefix_parts

############### Define the type of the routing software ###############

router_type = RouterAgentType.FRR

############### Load configurations from files ###############

# Load the local network configuration, 
# which is related to the BGP software configuration
from vnet_config import VNET_CONFIG
# Load the test side configuration
BGP_CONFIG : BGPToolkitConfiguration = parse_bgp_config_from_yaml(
    "config/bgp_config.yaml"
)

############### Configure the basic parameters ###############

router_agent = VNET_CONFIG["router_software"]
tester_agent = VNET_CONFIG["clients"][0]
exabgp_agent = VNET_CONFIG["clients"][1]

tester_agent_namespace = tester_agent["namespace"]
exabgp_agent_namespace = exabgp_agent["namespace"]

router_agent_ip, _ = get_ipv4_prefix_parts(router_agent["ip"])
tester_agent_ip, _ = get_ipv4_prefix_parts(tester_agent['ip'])
exabgp_agent_ip, _ = get_ipv4_prefix_parts(exabgp_agent['ip'])

tester_agent_identifier = BGP_CONFIG.bgp_identifier

router_agent_asn = 65001
tester_agent_asn = BGP_CONFIG.asn
exabgp_agent_asn = 65003

###### Check the validity of the configuration ######

# The tester's IP and BGP identifier should be consistent
if tester_agent_ip != tester_agent_identifier:
    print(f"Warning: The BGP tester's ip ({tester_agent_ip}) and BGP identifier {tester_agent_identifier} are not consistent!")
# The routing software's, tester's, and exabgp agent's ASN should all be different.
if router_agent_asn==tester_agent_asn or exabgp_agent_asn==tester_agent_asn:
    raise ValueError(f"The AS number of the tester agent {tester_agent_asn} should not be the same as the router software's or the ExaBGP agent's!")

############### Configure the interfaces ###############

# Configure the TCP agent
tcp_agent_config = TCPAgentConfiguration(host=router_agent_ip,
                                          port=179,
                                          bind_val=(tester_agent_ip, 0),
                                          netns=tester_agent_namespace)
# Configure the ExaBGP agent
exabgp_agent_config = ExaBGPAgentConfiguration(namespace=exabgp_agent_namespace)
# Generate the configuration file for the ExaBGP agent
generate_exabgp_config(peer_ip_addr=router_agent_ip,
                       peer_asn=router_agent_asn,
                       local_ip_addr=exabgp_agent_ip,
                       local_asn=exabgp_agent_asn,
                       output_file="config/exabgp.conf")
