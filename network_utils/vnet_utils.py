"""
This file is used to define the functions used to built up the virtual network within the host. 
"""

import os

def peer_name(name:str):
    """Calculate the default peer name of a veth interface."""
    return name + "-peer"

########## Commands for virtual network bridges ##########

def create_network_bridge(name: str):
    """Create a network bridge."""
    return f'sudo ip link add name {name} type bridge'

def start_network_bridge(name: str):
    """Start the network bridge."""
    return f"sudo ip link set {name} up"

def close_network_bridge(name: str):
    """Close the network bridge."""
    return f"sudo ip link set {name} down"

def delete_network_bridge(name: str):
    """Delete the network bridge."""
    return f"sudo ip link delete {name} type bridge"

########## Commands for veth ##########

def create_veth(name: str,
                peer_name: str = None):
    """Create a veth."""
    peer_name = peer_name(name) if peer_name is None else peer_name
    return f"sudo ip link add {name} type veth peer name {peer_name}"

def start_veth(name: str):
    """
    Start a veth interface.
    Notice that this method can only start one side of the interfaces,
    while the veth need both sides up to work. 
    """
    return f"sudo ip link set {name} up"

def close_veth(name: str):
    """
    Close a veth interface.
    Notice that this method can only close one side of the interfaces.
    """
    return f"sudo ip link set {name} down"

def delete_veth(name: str):
    """
    Delete the veth.
    Both sides of the veth connection will be deleted.
    """
    return f"sudo ip link delete {name}"

def assign_prefix_to_interface(prefix: str,
                               interface_name: str):
    """"Assign an IP prefix to the network interface."""
    return f"sudo ip addr add {prefix} dev {interface_name}"

def delete_assigned_prefix_for_interface(prefix: str,
                                         interface_name: str):
    """Delete the assigned IP prefix for the network interface."""
    return f"sudo ip addr del {prefix} dev {interface_name}"

def bind_veth_to_bridge(veth_name: str,
                        bridge_name: str):
    """Bind one side of the veth to the bridge."""
    return f"sudo ip link set {veth_name} master {bridge_name}"

def unbind_veth(veth_name: str):
    """Unbind the veth interface."""
    return f"sudo ip link set {veth_name} nomaster"

########## Commands for virtual network namespace ##########

def create_network_namespace(name: str):
    """Create a network namespace."""
    return f"sudo ip netns add {name}"

def delete_network_namespace(name: str):
    """Delete the network namespace."""
    return f"sudo ip netns delete {name}"

def bind_interface_with_network_namespace(interface_name: str,
                                          namespace_name: str):
    """Bind the interface with the network namespace."""
    return f"sudo ip link set {interface_name} netns {namespace_name}"

def unbind_interface_with_network_namespace(interface_name: str,
                                            namespace_name: str):
    """Unbind the interface with the network namespace."""
    return f"sudo ip netns exec {namespace_name} ip link set {interface_name} netns 1"

def execute_under_namespace(command: str,
                            namespace: str = None):
    """Execute the command under given network namespace."""
    prefix = f"sudo ip netns exec {namespace} " if namespace is not None else ""
    final_command = prefix + command
    os.system(final_command)
