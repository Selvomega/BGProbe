"""
The OpenBGPD router. 
"""

from .basic_types import *
from .router_agent_base import BaseRouterAgent
from basic_utils.file_utils import read_file, clear_file, delete_file
from time import sleep
from basic_utils.const import REPO_ROOT_PATH
from tomlkit import parse, dumps
import subprocess, re

OPENBGPD_CONF = "/usr/local/etc/bgpd.conf"
OPENBGPD_CONF_MARKER = "###### Configure below ######"
OPENBGPD_LOG = "/var/log/bgpd.log"

class OpenBGPDRouterAgent(BaseRouterAgent):
    """
    The agent interface for OpenBGPD router.
    """

    ########## Initialization ##########

    def __init__(self, configuration : RouterAgentConfiguration):
        """
        Initialize the BGP router. 
        """
        if configuration.get_router_type() != RouterAgentType.OPENBGPD:
            raise ValueError(f"Initializing OpenBGPD router with router type {configuration.get_router_type()}!")
        self.router_agent_type : RouterAgentType = RouterAgentType.OPENBGPD
        self.router_agent_configuration : RouterAgentConfiguration = configuration
    
    ########## Turn on/off the instance ##########

    def start_bgp_instance(self):
        """
        Start the BGP instance using `self.router_agent_configuration` 
        """

        global_conf = f"""
AS {self.router_agent_configuration.asn}
router-id 10.0.0.127

allow from any
allow to any

listen on 127.0.0.1
listen on 10.0.0.127
log updates
"""
        neighbor_conf_list = []
        for neighbor in self.router_agent_configuration.neighbors:
            neighbor_conf = f"""
neighbor {neighbor.peer_ip} {{
    remote-as               {neighbor.peer_asn}
    announce IPv4           unicast
    announce IPv6           none
    announce extended message yes
    local-address           10.0.0.127
    passive
}}
"""
            neighbor_conf_list.append(neighbor_conf)
        overall_conf = global_conf + "".join(neighbor_conf_list)
        # Clear the old bgpd process
        os.system("sudo pkill bgpd")
        # Edit OpenBGPD config file.
        with open(OPENBGPD_CONF, 'r') as f:
            lines = f.readlines()
        found = False
        for i, line in enumerate(lines):
            if line.strip() == OPENBGPD_CONF_MARKER.strip():
                found = True
                break
        if not found:
            raise ValueError(f"OpenBGPD configuration file marker not found! ({OPENBGPD_CONF_MARKER})")
        new_lines = lines[:i+1] + ['\n' + overall_conf + '\n']
        # Write the configuration file of BIRD
        with open(OPENBGPD_CONF, 'w') as f:
            f.writelines(new_lines)

        os.system("sudo -E bgpd -v")
    
    def end_bgp_instance(self):
        """
        Shut down the BGP instance
        """
        os.system("sudo pkill bgpd")

    def restart_bgp_instance(self):
        """
        Restart the BGP instance.
        """
        raise NotImplementedError("`restart_bgp_instance` not implemented!")
    
    ########## OpenBGPD config file management ##########

    def message_mrt_dump_config(self, path: str):
        """
        Modify the config file for message MRT dumping.
        """
        dump_allin_pattern = re.compile(r'^dump all in\s+"([^"]+)"\s+(\d+)\s*$')
        with open(OPENBGPD_CONF, "r") as f:
            lines = f.readlines()
        if OPENBGPD_CONF_MARKER in (line.strip() for line in lines):
            marker_index = next(
                i for i, line in enumerate(lines) if OPENBGPD_CONF_MARKER in line
            )
        else:
            marker_index = len(lines)
        found_allin = False
        for i in range(marker_index):
            if dump_allin_pattern.match(lines[i]):
                lines[i] = f'dump all in "{path}" 300\n'
                found_allin = True
        inserts = []
        if not found_allin:
            inserts.append(f'dump all in "{path}" 300\n')

        lines = inserts + lines
        with open(OPENBGPD_CONF, "w") as f:
            f.writelines(lines)
        
        
    def route_mrt_dump_config(self, path: str):
        """
        Modify the config file for route MRT dumping.
        """
        dump_tablev2_pattern = re.compile(r'^dump table-v2\s+"([^"]+)"\s+(\d+)\s*$')
        with open(OPENBGPD_CONF, "r") as f:
            lines = f.readlines()
        if OPENBGPD_CONF_MARKER in (line.strip() for line in lines):
            marker_index = next(
                i for i, line in enumerate(lines) if OPENBGPD_CONF_MARKER in line
            )
        else:
            marker_index = len(lines)
        found_tablev2 = False
        for i in range(marker_index):
            if dump_tablev2_pattern.match(lines[i]):
                lines[i] = f'dump table-v2 "{path}" 1\n'
                found_tablev2 = True
        inserts = []
        if not found_tablev2:
            inserts.append(f'dump table-v2 "{path}" 1\n')

        lines = inserts + lines
        with open(OPENBGPD_CONF, "w") as f:
            f.writelines(lines)
    
    ########## Log manipulation ##########

    def read_log(self):
        """
        Read (all) the content from the routing softwares' log.
        Must execute with sudo-command.
        """
        return read_file(OPENBGPD_LOG)

    def clear_log(self):
        """
        Clear the content from the routing softwares' log.
        Must execute with sudo-command.
        """
        clear_file(OPENBGPD_LOG)
    
    ########## Crash management ##########
    
    @classmethod
    def if_crashed(cls) -> bool:
        """
        Return if the router software has crashed.
        """
        # Get all process
        ps_output = subprocess.check_output(["ps", "aux"]).decode("utf-8")

        # find OpenBGPD
        lines = [line for line in ps_output.split("\n") 
                if "bgpd" in line and "grep" not in line and line.strip() != ""]

        # Check if there is real OpenBGPD process
        for line in lines:
            if re.search(r"bgpd", line):  # match bgpd
                # OpenBGPD is running.
                return False

        # OpenBGPD is NOT running.
        return True

    def recover_from_crash(self):
        """
        Recover the software from crash.
        Do NOTHING here because the daemon and instance of OpenBGPD are as a whole.
        """
        return
    
    def restart_software(self):
        """
        Restart the software.
        Do NOTHING here because the daemon and instance of OpenBGPD are as a whole.
        """
        return
