"""
The frr router. 
"""

from .basic_types import *
from .router_base import BaseRouter
from time import sleep
import subprocess

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
            # Use this command to allow ingress/egress without policy configuration.
            "no bgp ebgp-requires-policy",
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

    ########## Crash management ##########

    def if_crashed(self) -> bool:
        """
        Return if the router software has crashed.
        """
        output = subprocess.getoutput("systemctl is-active frr")
        return output!="active"

    def recover_from_crash(self):
        """
        Recover the software from crash.
        """
        started = not self.if_crashed()
        counter = 0
        while not started:
            os.system("sudo systemctl start frr")
            sleep(0.5)
            started = not self.if_crashed()
            counter  = counter + 1
            if counter>=5:
                raise ValueError("Restarting FRRouting failed for 5 times.")

    ########## Other utils ##########

    def wait_for_log(self, time_duration: float = 0.1):
        """
        Waiting until the log does not update anymore.
        """
        no_updates = False
        prev_content = None
        while not no_updates:
            cur_content = self.read_log()
            no_updates = prev_content==cur_content
            prev_content = cur_content
            sleep(time_duration) # Sleep for 0.1 second

            # if not no_updates:
            #     print("For debug")
            #     print(f"Previous content:\n{prev_content}\nCurrent content:\n{cur_content}")
