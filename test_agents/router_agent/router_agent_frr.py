"""
The FRR router. 
"""

from .basic_types import *
from .router_agent_base import BaseRouterAgent
from basic_utils.file_utils import read_file, clear_file
from time import sleep
import subprocess, os, time

FRR_LOG = "/var/log/frr/bgpd.log"

class FRRRouterAgent(BaseRouterAgent):
    """
    The interface for FRR router.
    """

    ########## Initialization ##########

    def __init__(self, configuration : RouterAgentConfiguration):
        """
        Initialize the BGP router. 
        """
        if configuration.get_router_type() != RouterAgentType.FRR:
            raise ValueError(f"Initializing FRR router with router type {configuration.get_router_type()}!")
        self.router_agent_type : RouterAgentType = RouterAgentType.FRR
        self.router_agent_configuration : RouterAgentConfiguration = configuration
    
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
        full_commands = FRRRouterAgent.FRR_CONFIG_TERMINAL + modified_commands
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
        full_commands = FRRRouterAgent.FRR_CONFIG_TERMINAL + [f"-c 'router bgp {self.router_agent_configuration.asn}'"] + modified_commands
        single_command = " ".join(full_commands)
        os.system(single_command)

    ########## Turn on/off the instance ##########

    def start_bgp_instance(self):
        """
        Start the BGP instance using `self.router_agent_configuration` 
        """
        config_debugging_info = [
            "debug bgp neighbor-events",
            "debug bgp updates",
            "debug bgp keepalives",
            "debug bgp nht"
        ]
        config_router_info = [
            # Initialize the BGP speaker
            f"router bgp {self.router_agent_configuration.asn}",
            # Use this command to allow ingress/egress without policy configuration.
            "no bgp ebgp-requires-policy",
            # Set the BGP router id
            f"bgp router-id {self.router_agent_configuration.router_id}"
        ]
        config_local_prefix = [
            # initialize the network prefixes
            f"network {prefix.get_str_expression()}" for prefix in self.router_agent_configuration.local_prefixes
        ]
        config_neighbor = [
            # initialize the BGP neighbors
            command for neighbor in self.router_agent_configuration.neighbors for command in [
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
        commands = [f"no router bgp {self.router_agent_configuration.asn}"]
        # execute the command
        self.execute_commands_in_config_level(commands=commands)

    def restart_bgp_instance(self):
        """
        Restart the BGP instance.
        """
        raise NotImplementedError("`restart_bgp_instance` not implemented!")
        
    ########## Dump MRT file ##########

    def dump_updates(self, path: str):
        """
        Dump only BGP updates messages to `path`.
        """
        self.execute_commands_in_config_level([f"dump bgp updates {path}"])

    # Old version of `dump_routing_table`
    # def dump_routing_table(self, path: str):
    #     """
    #     Dump the whole BGP routing table to `path`.
    #     """
    #     self.execute_commands_in_config_level([f"dump bgp routes-mrt {path}"])

    def dump_routing_table(self, path: str):
        """
        Dump the whole BGP routing table to `path`, with a 3 second timeout.
        Timeout if the file size keep growing
        """
        self.execute_commands_in_config_level([f"dump bgp routes-mrt {path}"])
        sleep(0.1)
        start_time = time.time()
        cur_size = 0
        prev_size = 0
        still_increasing = True
        while time.time() - start_time < 3:
            cur_size = os.path.getsize(path)
            if cur_size != prev_size:
                sleep(0.1)
            else:
                still_increasing = False
                break
            prev_size = cur_size
        if still_increasing:
            # If the file size keeps increasing
            os.system("sudo pkill -9 frr")
            os.system("sudo pkill -9 bgpd")
    
    def stop_dump_updates(self):
        """
        Stop `dump_updates`.
        """
        self.execute_commands_in_config_level(["no dump bgp updates"])

    def stop_dump_routing_table(self):
        """
        Stop `dump_routing_table`.
        """
        self.execute_commands_in_config_level(["no dump bgp routes-mrt"])

    ########## Log manipulation ##########

    def read_log(self):
        """
        Read (all) the content from the routing softwares' log.
        Must execute with sudo-command.
        """
        return read_file(FRR_LOG)

    def clear_log(self):
        """
        Clear the content from the routing softwares' log.
        Must execute with sudo-command.
        """
        clear_file(FRR_LOG)

    ########## Crash management ##########

    @classmethod
    def if_crashed(cls) -> bool:
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
    
    def restart_software(self):
        """
        Restart the software.
        """
        os.system("sudo systemctl reset-failed frr.service")
        os.system("sudo systemctl restart frr")
        sleep(0.5)

   
    ########## Modification, derpecated ##########

    # def append_local_prefix(self, prefix):
    #     """
    #     Add a local prefix to the router.
    #     The base class will append the prefix to the configuration.
    #     You should call `super().append_local_prefix(prefix)`.
    #     """
    #     # Call the super method first
    #     make_modification = super().append_local_prefix(prefix)
    #     # Then make modification to the router instance
    #     if make_modification:
    #         commands = [
    #             f"network {prefix}"
    #         ]
    #         self.execute_commands_in_router_level(commands)

    # def remove_local_prefix(self, prefix):
    #     """
    #     Reove a local prefix to the router.
    #     The base class will remove the prefix to the configuration.
    #     You should call `super().remove_local_prefix(prefix)`.
    #     """
    #     # Call the super method first
    #     make_modification = super().remove_local_prefix(prefix)
    #     # Then make modification to the router instance
    #     if make_modification:
    #         commands = [
    #             f"no network {prefix}"
    #         ]
    #         self.execute_commands_in_router_level(commands)
    
    # def append_neighbor(self, neighbor):
    #     """
    #     Add a neighbor to the router.
    #     The base class will append the prefix to the configuration.
    #     You should call `super().append_neighbor(neighbor)`.
    #     """
    #     # Call the super method first
    #     make_modification = super().append_neighbor(neighbor)
    #     # Then make modification to the router instance
    #     if make_modification:
    #         commands = [
    #             command for neighbor in self.router_agent_configuration.neighbors for command in [
    #                 f"neighbor {neighbor.peer_ip} remote-as {neighbor.peer_asn}",
    #                 f"neighbor {neighbor.peer_ip} update-source {neighbor.local_source}"
    #             ]
    #         ]
    #         self.execute_commands_in_router_level(commands)
    
    # def remove_neighbor(self, neighbor):
    #     """
    #     Reove a neighbor from the router.
    #     The base class will remove the prefix to the configuration.
    #     You should call `super().remove_neighbor(neighbor)`.
    #     """
    #     # Call the super method first
    #     make_modification = super().append_neighbor(neighbor)
    #     # Then make modification to the router instance
    #     if make_modification:
    #         commands = [
    #             f"no neighbor {neighbor.peer_ip} remote-as {neighbor.peer_asn}"
    #         ]
    #         self.execute_commands_in_router_level(commands)
