"""
The frr router. 
"""

from .basic_types import *
from .router_base import BaseRouter

class FRRRouter(BaseRouter):
    """
    The interface for FRR router.
    """

    def __init__(self, configuration : RouterConfiguration):
        """
        Initialize the BGP router. 
        """
        self.software_type : RouterSoftwareType = RouterSoftwareType.FRR
        self.router_configuration : RouterConfiguration = configuration
    
    # This should be attached to the begining of the command you want to execute.
    FRR_CONFIG_TERMINAL = [
        "sudo vtysh",
        "-c 'configure terminal'"
    ]

    def execute_commands_in_config_level(self, commands: list[str]):
        """
        Execute the commands in the `configure terminal` level
        the `commands` should be a list of the commands you want to execute
        no need to care about the `sudo vtysh -c` stuff...
        """
        modified_commands = [
            f"-c '{command}'" for command in commands
        ]
        full_commands = FRRRouter.FRR_CONFIG_TERMINAL + modified_commands
        single_command = " ".join(full_commands)
        os.system(single_command)
    
    def execute_commands_in_router_level(self, commands: list[str]):
        """
        Execute the commands in the `router bgp <asn>` level
        the `commands` should be a list of the commands you want to execute
        no need to care about the `sudo vtysh -c` stuff...
        """
        modified_commands = [
            f"-c '{command}'" for command in commands
        ]
        full_commands = FRRRouter.FRR_CONFIG_TERMINAL + [f"-c 'router bgp {self.router_configuration.asn}'"] + modified_commands
        single_command = " ".join(full_commands)
        os.system(single_command)

    def start_bgp_instance(self):
        """
        Start the BGP instance using `self.router_configuration` 
        """
        config_debugging_info = [
            "debug bgp neighbor-events",
            "debug bgp updates",
            "debug bgp nht"
        ]
        config_router_info = [
            # Initialize the BGP speaker
            f"router bgp {self.router_configuration.asn}",
            # Set the BGP router id
            f"bgp router-id {self.router_configuration.router_id.value}"
        ]
        config_local_prefix = [
            # initialize the network prefixes
            f"network {prefix.get_str_expression()}" for prefix in self.router_configuration.local_prefixes
        ]
        config_neighbor = [
            # initialize the BGP neighbors
            f"neighbor {neighbor.peer_ip.get_str_expression()} remote-as {neighbor.peer_asn}" for neighbor in self.router_configuration.neighbors
        ]
        commands = config_debugging_info + config_router_info + config_local_prefix + config_neighbor
        # execute the command
        self.execute_commands_in_config_level(commands=commands)
    
    def end_bgp_instance(self):
        """
        Shut down the BGP instance
        """
        commands = [f"no router bgp {self.router_configuration.asn}"]
        # execute the command
        self.execute_commands_in_config_level(commands=commands)

    def restart_bgp_instance(self):
        """
        Restart the BGP instance.
        """
        raise NotImplementedError("`restart_bgp_instance` not implemented!")
    
    def append_local_prefix(self, prefix):
        """
        Add a local prefix to the router.
        The base class will append the prefix to the configuration.
        You should call `super().append_local_prefix(prefix)`.
        """
        # Call the super method first
        make_modification = super().append_local_prefix(prefix)
        # Then make modification to the router instance
        if make_modification:
            commands = [
                f"network {prefix.get_str_expression()}"
            ]
            self.execute_commands_in_router_level(commands)

    def remove_local_prefix(self, prefix):
        """
        Reove a local prefix to the router.
        The base class will remove the prefix to the configuration.
        You should call `super().remove_local_prefix(prefix)`.
        """
        # Call the super method first
        make_modification = super().remove_local_prefix(prefix)
        # Then make modification to the router instance
        if make_modification:
            commands = [
                f"no network {prefix.get_str_expression()}"
            ]
            self.execute_commands_in_router_level(commands)
    
    def append_neighbor(self, neighbor):
        """
        Add a neighbor to the router.
        The base class will append the prefix to the configuration.
        You should call `super().append_neighbor(neighbor)`.
        """
        # Call the super method first
        make_modification = super().append_neighbor(neighbor)
        # Then make modification to the router instance
        if make_modification:
            commands = [
                f"neighbor {neighbor.peer_ip.get_str_expression()} remote-as {neighbor.peer_asn}"
            ]
            self.execute_commands_in_router_level(commands)
    
    def remove_neighbor(self, neighbor):
        """
        Reove a neighbor from the router.
        The base class will remove the prefix to the configuration.
        You should call `super().remove_neighbor(neighbor)`.
        """
        # Call the super method first
        make_modification = super().append_neighbor(neighbor)
        # Then make modification to the router instance
        if make_modification:
            commands = [
                f"no neighbor {neighbor.peer_ip.get_str_expression()} remote-as {neighbor.peer_asn}"
            ]
            self.execute_commands_in_router_level(commands)
