"""
The GoBGP router. 
"""

from .basic_types import *
from .router_agent_base import BaseRouterAgent
from basic_utils.file_utils import read_file, clear_file, delete_file
from time import sleep
from basic_utils.const import REPO_ROOT_PATH
from tomlkit import parse, dumps
import subprocess, re

GOBGP_CONF = f"{REPO_ROOT_PATH}/config/gobgpd.conf"
GOBGP_CONF_MARKER = "###### Configure below ######"
GOBGP_LOG = f"{REPO_ROOT_PATH}/data/gobgp.log"

class GoBGPRouterAgent(BaseRouterAgent):
    """
    The agent interface for GoBGP router.
    """

    ########## Initialization ##########

    def __init__(self, configuration : RouterAgentConfiguration):
        """
        Initialize the BGP router. 
        """
        if configuration.get_router_type() != RouterAgentType.GOBGP:
            raise ValueError(f"Initializing GoBGP router with router type {configuration.get_router_type()}!")
        self.router_agent_type : RouterAgentType = RouterAgentType.GOBGP
        self.router_agent_configuration : RouterAgentConfiguration = configuration

    ########## Turn on/off the instance ##########

    def start_bgp_instance(self):
        """
        Start the BGP instance using `self.router_agent_configuration` 
        """
        global_conf = f"""
[global.config]
  as = {self.router_agent_configuration.asn}
  router-id = "10.0.0.127"
  [global.apply-policy.config]
    import-policy-list = ["only-from-neighbors"]
    default-import-policy = "reject-route"
"""
        only_allow_neighboring_as_policy = f"""
[[defined-sets.bgp-defined-sets.as-path-sets]]
  as-path-set-name = "neighboring-as"
  as-path-list = {["^"+str(neighbor.peer_asn) for neighbor in self.router_agent_configuration.neighbors]}

[[policy-definitions]]
  name = "only-from-neighbors"
  [[policy-definitions.statements]]
    [policy-definitions.statements.conditions.bgp-conditions.match-as-path-set]
      as-path-set = "neighboring-as"
    [policy-definitions.statements.actions]
      route-disposition = "accept-route"
"""
        neighbor_conf_list = []
        for neighbor in self.router_agent_configuration.neighbors:
            neighbor_conf = f"""
[[neighbors]]
  [neighbors.config]
    neighbor-address = "{neighbor.peer_ip}"
    peer-as = {neighbor.peer_asn}
  [neighbors.transport.config]
    passive-mode = true
    ttl = 64  # default value on Linux
  [neighbors.ebgp-multihop.config]
    enabled = false #directly connection should be set false, if not, peer will be deleted after hold-time
    multihop-ttl = 100
"""
            neighbor_conf_list.append(neighbor_conf)
        overall_conf = global_conf + only_allow_neighboring_as_policy + "".join(neighbor_conf_list)
        
        # Remove the old log file
        delete_file(GOBGP_LOG)
        # Clear the old gobgpd process
        os.system("sudo pkill gobgp")
        # Edit GoBGP config file.
        with open(GOBGP_CONF, 'r') as f:
            lines = f.readlines()
        found = False
        for i, line in enumerate(lines):
            if line.strip() == GOBGP_CONF_MARKER.strip():
                found = True
                break
        if not found:
            raise ValueError(f"GoBGP configuration file marker not found! ({GOBGP_CONF_MARKER})")
        new_lines = lines[:i+1] + ['\n' + overall_conf + '\n']
        # Write the configuration file of BIRD
        with open(GOBGP_CONF, 'w') as f:
            f.writelines(new_lines)
        
        os.system(f"nohup sudo -E gobgpd -f {GOBGP_CONF} -p -l debug > {GOBGP_LOG} &")
        sleep(0.5)
    
    def end_bgp_instance(self):
        """
        Shut down the BGP instance
        """
        os.system("sudo pkill gobgp")

    def restart_bgp_instance(self):
        """
        Restart the BGP instance.
        """
        raise NotImplementedError("`restart_bgp_instance` not implemented!")
    
    ########## GoBGP config file management ##########

    def message_mrt_dump_config(self, path: str):
        """
        Modify the config file for message MRT dumping.
        """
        with open(GOBGP_CONF, "r") as f:
            config = parse(f.read())
        for entry in config["mrt-dump"]:
            if entry["config"]["dump-type"] == "updates":
                entry["config"]["file-name"] = path
        with open(GOBGP_CONF, "w") as f:
            f.write(dumps(config))

    def route_mrt_dump_config(self, path: str):
        """
        Modify the config file for route MRT dumping.
        """
        with open(GOBGP_CONF, "r") as f:
            config = parse(f.read())
        for entry in config["mrt-dump"]:
            if entry["config"]["dump-type"] == "table":
                entry["config"]["file-name"] = path
        with open(GOBGP_CONF, "w") as f:
            f.write(dumps(config))
    
    ########## Log manipulation ##########

    def read_log(self):
        """
        Read (all) the content from the routing softwares' log.
        Must execute with sudo-command.
        """
        return read_file(GOBGP_LOG)

    def clear_log(self):
        """
        Clear the content from the routing softwares' log.
        Must execute with sudo-command.
        """
        clear_file(GOBGP_LOG)
    
    ########## Crash management ##########
    
    @classmethod
    def if_crashed(cls) -> bool:
        """
        Return if the router software has crashed.
        """
        # Get all process
        ps_output = subprocess.check_output(["ps", "aux"]).decode("utf-8")

        # find GoBGP
        lines = [line for line in ps_output.split("\n") 
                if "gobgp" in line and "grep" not in line and line.strip() != ""]

        # Check if there is real GoBGP process
        for line in lines:
            if re.search(r"gobgp", line):  # match gobgp
                # GoBGP is running.
                return False

        # GoBGP is NOT running.
        return True

    def recover_from_crash(self):
        """
        Recover the software from crash.
        Do NOTHING here because the daemon and instance of GoBGP are as a whole.
        """
        return
    
    def restart_software(self):
        """
        Restart the software.
        Do NOTHING here because the daemon and instance of GoBGP are as a whole.
        """
        return
