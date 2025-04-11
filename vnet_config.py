from network_utils.vnet_utils import *

import re, sys

########## Function for parsing the config file ##########

def parse_yaml(path):
    config = {}
    with open(path, 'r') as file:
        yaml_content = file.read()

        # Extract the key-value pair using the regex. 
        bridge_match = re.search(r"bridge:\s*(\S+)", yaml_content)
        if bridge_match:
            config["bridge"] = bridge_match.group(1)

        router_match = re.search(r"router_software:\s*\n\s*ip:\s*(\S+)\s*\n\s*veth:\s*(\S+)", yaml_content)
        if router_match:
            config["router_software"] = {
                "ip": router_match.group(1),
                "veth": router_match.group(2)
            }

        clients_match = re.findall(r"namespace:\s*(\S+)\s*\n\s*ip:\s*(\S+)\s*\n\s*veth:\s*(\S+)", yaml_content)
        if clients_match:
            config["clients"] = [
                {
                    "namespace": client[0], 
                    "ip": client[1], 
                    "veth": client[2]
                } for client in clients_match
            ]

    return config

########## Function for setting up th vnet ##########

def set_up_vnet(config):
    """
    Set up the virtual network configuration.
    """
    bridge_name = config["bridge"]
    router_software: dict = config["router_software"]
    # `clients` is a list of dictionaries
    clients: list = config["clients"]
    # Use a shorter expression
    exec_ns = execute_under_namespace

    ###### Processing the network bridge ######

    # Create the network bridge
    exec_ns(create_network_bridge(bridge_name))
    # Start the network bridge
    exec_ns(start_network_bridge(bridge_name))

    ###### Processing the router software's veth ######

    # Create the veth for the router instance
    exec_ns(create_veth(router_software["veth"],
                        peer_name(router_software["veth"])))
    # Bind the peer side of the router's veth into the bridge.
    exec_ns(bind_veth_to_bridge(peer_name(router_software["veth"]),
                                bridge_name))
    # Start both sides of the router's veth.
    exec_ns(start_veth(router_software["veth"]))
    exec_ns(start_veth(peer_name(router_software["veth"])))
    # Assign the adress for the router 
    exec_ns(assign_prefix_to_interface(router_software["ip"],
                                       router_software["veth"]))

    ###### Processing the clients' veth ######

    for client in clients:
        # First start the network namespace.
        exec_ns(create_network_namespace(client["namespace"]))
        # Create the veth for the client
        exec_ns(create_veth(client["veth"],
                            peer_name(client["veth"])))
        # Bind the peer side of the client's veth into the bridge.
        exec_ns(bind_veth_to_bridge(peer_name(client["veth"]),
                                    bridge_name))
        # Bind the original side of the client's veth into the namespace.
        exec_ns(bind_interface_with_network_namespace(client["veth"],
                                                      client["namespace"]))
        # Start both sides of the client's veth.
        # First start the peer side,
        exec_ns(start_veth(peer_name(client["veth"])))
        # then start the original side.
        exec_ns(start_veth(client["veth"]),
                namespace=client["namespace"])
        # Assign the adress for the client 
        exec_ns(assign_prefix_to_interface(client["ip"],
                                           client["veth"]),
                namespace=client["namespace"])

########## Function for tearing down th vnet ##########

def cleanup_namespaces(config: dict):
    """Clean all namespaces."""
    # Get all namespaces
    # `clients` is a list of dictionaries
    clients: list = config["clients"]
    # Use a shorter expression
    exec_ns = execute_under_namespace
    namespaces = [client["namespace"] for client in clients]
    for namespace in namespaces:
        exec_ns(delete_network_namespace(namespace))

def cleanup_veth_interfaces(config: dict):
    """
    Clean all veth interfaces.
    Important: The veth name must contain `veth`!
    """
    # Get all veth interfaces
    router_software: dict = config["router_software"]
    # `clients` is a list of dictionaries
    clients: list = config["clients"]
    # Use a shorter expression
    exec_ns = execute_under_namespace
    veths = [router_software["veth"]] + [
        client["veth"] for client in clients
    ]
    for veth in veths:
        exec_ns(delete_veth(veth))

def cleanup_bridges(config: dict):
    # Get the bridge used
    bridge_name = config["bridge"]
    # Use a shorter expression
    exec_ns = execute_under_namespace
    exec_ns(delete_network_bridge(bridge_name))

def tear_down_vnet(config: dict):
    """
    Tear down the vnet.
    The `config` should be `VNET_CONFIG`.
    """
    cleanup_namespaces(config)
    cleanup_veth_interfaces(config)
    cleanup_bridges(config)

########## vnet configuration ##########

# Parse the yaml file
# This can be used by other files
VNET_CONFIG = parse_yaml("vnet_config.yaml")

########## main function ##########

if __name__ == "__main__":

    import json
    print(json.dumps(VNET_CONFIG, indent=4))

    if len(sys.argv) != 2:
        print("Format: python3 vnet_config.py [up|down|null]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "up":
        set_up_vnet(VNET_CONFIG)
    elif command == "down":
        tear_down_vnet(VNET_CONFIG)
    elif command == "null":
        pass
    else:
        print("Please enter 'up', 'down' or 'null'")
        sys.exit(1)
