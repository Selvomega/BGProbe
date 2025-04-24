"""
The frr router. 
"""

from .basic_types import *
from .router_base import BaseRouter

class FRRRouter(BaseRouter):
    """
    The interface for FRR router.
    """

    ########## Initialization ##########

    def __init__(self, configuration : RouterConfiguration):
        """
        Initialize the BGP router. 
        """
        if configuration.get_router_type() != RouterSoftwareType.FRR:
            raise ValueError(f"Initializing FRR router with router type {configuration.get_router_type()}!")
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

    ########## Turn on/off the instance ##########

    def start_bgp_instance(self):
        """
        Start the BGP instance using `self.router_configuration` 
        """
        config_debugging_info = [
            "debug bgp neighbor-events",
            "debug bgp updates",
            "debug bgp keepalives",
            "debug bgp nht"
        ]
        config_router_info = [
            # Initialize the BGP speaker
            f"router bgp {self.router_configuration.asn}",
            # Set the BGP router id
            f"bgp router-id {self.router_configuration.router_id}"
        ]
        config_local_prefix = [
            # initialize the network prefixes
            f"network {prefix.get_str_expression()}" for prefix in self.router_configuration.local_prefixes
        ]
        config_neighbor = [
            # initialize the BGP neighbors
            command for neighbor in self.router_configuration.neighbors for command in [
                f"neighbor {neighbor.peer_ip} remote-as {neighbor.peer_asn}",
                f"neighbor {neighbor.peer_ip} update-source {neighbor.local_source}"
            ]
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

    ########## Modification ##########

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
                f"network {prefix}"
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
                f"no network {prefix}"
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
                command for neighbor in self.router_configuration.neighbors for command in [
                    f"neighbor {neighbor.peer_ip} remote-as {neighbor.peer_asn}",
                    f"neighbor {neighbor.peer_ip} update-source {neighbor.local_source}"
                ]
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
                f"no neighbor {neighbor.peer_ip} remote-as {neighbor.peer_asn}"
            ]
            self.execute_commands_in_router_level(commands)

    ########## Log manipulation ##########

    def read_log(self):
        """
        Read (all) the content from the routing softwares' log.
        Must execute with sudo-command.
        """
        return super().read_log("/var/log/frr/bgpd.log")

    def clear_log(self):
        """
        Clear the content from the routing softwares' log.
        Must execute with sudo-command.
        """
        super().clear_log("/var/log/frr/bgpd.log")
