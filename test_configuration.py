# This file defines the variables used to configure the test.

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bgp_utils.bgp_configuration import BGP_Configuration, parse_bgp_config_from_yaml
from test_agent.exabgp_agent import generate_exabgp_config, ExaBGPClientConfiguration
from network_utils.tcp_client import TCPClientConfiguration
from network_utils.utils import get_ipv4_prefix_parts
from routing_software_interface.basic_types import RouterConfiguration, Neighbor

############### Load configurations from files ###############

# Load the local network configuration, 
# which is related to the BGP software configuration
from vnet_config import VNET_CONFIG
# Load the test side configuration
BGP_CONFIG : BGP_Configuration = parse_bgp_config_from_yaml(
    "config/bgp_config.yaml"
)

############### Configure the basic parameters ###############

router_software = VNET_CONFIG["router_software"]
tester_client = VNET_CONFIG["clients"][0]
exabgp_client = VNET_CONFIG["clients"][1]

tester_client_namespace = tester_client["namespace"]
exabgp_client_namespace = exabgp_client["namespace"]

router_software_ip, _ = get_ipv4_prefix_parts(router_software["ip"])
tester_client_ip, _ = get_ipv4_prefix_parts(tester_client['ip'])
exabgp_client_ip, _ = get_ipv4_prefix_parts(exabgp_client['ip'])

tester_client_identifier = BGP_CONFIG.bgp_identifier

router_software_asn = 65001
tester_client_asn = BGP_CONFIG.asn
exabgp_client_asn = 65003

###### Check the validity of the configuration ######

# The tester's IP and BGP identifier should be consistent
if tester_client_ip != tester_client_identifier:
    print(f"Warning: The BGP tester's ip ({tester_client_ip}) and BGP identifier {tester_client_identifier} are not consistent!")
# The routing software's, tester's, and exabgp client's ASN should all be different.
if router_software_asn==tester_client_asn or exabgp_client_asn==tester_client_asn:
    raise ValueError(f"The AS number of the tester client {tester_client_asn} should not be the same as the router software's or the ExaBGP client's!")

############### Configure the interfaces ###############

# Configure the router software
router_config = RouterConfiguration(
    asn=router_software_asn,
    router_id=router_software_ip,
    neighbors=[
        Neighbor(
            peer_ip=tester_client_ip,
            peer_asn=tester_client_asn,
            local_source=router_software["veth"]
        ),
        Neighbor(
            peer_ip=exabgp_client_ip,
            peer_asn=exabgp_client_asn,
            local_source=router_software["veth"]
        ),
    ],
)
# Configure the TCP client
tcp_client_config = TCPClientConfiguration(host=router_software_ip,
                                           port=179,
                                           bind_val=(tester_client_ip, 0),
                                           netns=tester_client_namespace)
# Configure the ExaBGP client
exabgp_client_config = ExaBGPClientConfiguration(namespace=exabgp_client_namespace)
# Generate the configuration file for the ExaBGP client
generate_exabgp_config(peer_ip_addr=router_software_ip,
                       peer_asn=router_software_asn,
                       local_ip_addr=exabgp_client_ip,
                       local_asn=exabgp_client_asn,
                       output_file="config/exabgp.conf")
