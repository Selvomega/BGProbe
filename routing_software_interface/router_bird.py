"""
The BIRD router. 
"""

from .basic_types import *
from .router_base import BaseRouter
from time import sleep
import subprocess, re

BIRD_CONF = "/etc/bird/bird.conf"
BIRD_CONF = "/usr/local/etc/bird.conf"
BIRD_CONF_MARKER = "###### Configure below ######"
BIRD_LOG = "/var/log/bird.log"

class BIRDRouter(BaseRouter):
    """
    The interface for BIRD router.
    """

    ########## Initialization ##########

    def __init__(self, configuration : RouterConfiguration):
        """
        Initialize the BGP router. 
        """
        if configuration.get_router_type() != RouterSoftwareType.BIRD:
            raise ValueError(f"Initializing BIRD router with router type {configuration.get_router_type()}!")
        self.software_type : RouterSoftwareType = RouterSoftwareType.BIRD
        self.router_configuration : RouterConfiguration = configuration
    
    ########## Turn on/off the instance ##########

    def start_bgp_instance(self):
        """
        Start the BGP instance using `self.router_configuration` 
        """

        # Preparing BIRD config file content.
        peer_count = 1
        neighbor_conf_list = []
        for neighbor in self.router_configuration.neighbors:
            neighbor_conf = f"""
protocol bgp peer{peer_count} {{
  debug all;
  mrtdump {{messages}};
  local as {self.router_configuration.asn};
  neighbor {neighbor.peer_ip} as {neighbor.peer_asn};
  enforce first as;
  enable extended messages on;
  interpret communities on;
  passive yes;
  ipv4 {{ import all; export all; }};
}}
"""
            neighbor_conf_list.append(neighbor_conf)
            peer_count = peer_count + 1
        overall_conf = "".join(neighbor_conf_list)
        
        # Edit BIRD config file.
        with open(BIRD_CONF, 'r') as f:
            lines = f.readlines()
        found = False
        for i, line in enumerate(lines):
            if line.strip() == BIRD_CONF_MARKER.strip():
                found = True
                break
        if not found:
            raise ValueError("BIRD configuration file marker not found! ({BIRD_CONF_MARKER})")
        new_lines = lines[:i+1] + ['\n' + overall_conf + '\n']
        # Write the configuration file of BIRD
        with open(BIRD_CONF, 'w') as f:
            f.writelines(new_lines)

        # Apply configuration
        self.config_instance()

    def end_bgp_instance(self):
        """
        Shut down the BGP instance
        """
        # Edit BIRD config file.
        with open(BIRD_CONF, 'r') as f:
            lines = f.readlines()
        found = False
        for i, line in enumerate(lines):
            if line.strip() == BIRD_CONF_MARKER.strip():
                found = True
                break
        if not found:
            raise ValueError("BIRD configuration file marker not found! ({BIRD_CONF_MARKER})")
        new_lines = lines[:i+1]
        # Write the configuration file of BIRD
        with open(BIRD_CONF, 'w') as f:
            f.writelines(new_lines)
        
        # Apply configuration
        self.config_instance()

    def restart_bgp_instance(self):
        """
        Restart the BGP instance.
        """
        raise NotImplementedError("`restart_bgp_instance` not implemented!")
    
    ########## BIRD config file management ##########

    def add_routes_mrt_config(self, dump_path: str):
        """
        Add the MRT config for dumping the routing table in the BIRD config file.
        """
        new_config = f'''protocol mrt {{
\ttable "master4";
\tfilename "{dump_path}";
\tperiod 1;
}}
'''
        with open(BIRD_CONF, 'r') as f:
            content = f.read()

        # Regex match protocol mrt { ... }
        pattern = re.compile(r'protocol\s+mrt\s*{[^}]*}', re.IGNORECASE | re.DOTALL)

        if pattern.search(content):
            # Why there is a `protocol mrt` configuration?
            print(f"Warning: There is a existing mrt protocol configuration:\n {content}")
            content = pattern.sub(new_config.strip(), content)
        else:
            # Append a configuration
            content = content.strip()
            content += '\n'
            content += '\n' + new_config.strip() + '\n'

        with open(BIRD_CONF, 'w') as f:
            f.write(content)
    
    def remove_routes_mrt_config(self):
        """
        Remove the MRT config for dumping the routing table in the BIRD config file.
        """
        with open(BIRD_CONF, "r") as f:
            content = f.read()

        # match the protocol mrt { ... } section
        pattern = re.compile(r'protocol\s+mrt\s*{[^}]*}', re.IGNORECASE | re.DOTALL)

        if pattern.search(content):
            content = pattern.sub('', content, count=1)
            content = re.sub(r'\n{2,}', '\n\n', content) 
            content = content.strip() + '\n'  # Maintain a newline in the end
            with open(BIRD_CONF, 'w') as f:
                f.write(content)

    def add_messages_mrt_config(self, dump_path: str):
        """
        Add the MRT config for dumping the BGP messages in the BIRD config file.
        """
        new_line = f'mrtdump "{dump_path}";'

        with open(BIRD_CONF, 'r') as f:
            content = f.read()

        # Find all protocol {...} sections
        protocol_blocks = [m.span() for m in re.finditer(r'protocol\s+\w+\s*{[^}]*}', content, re.DOTALL | re.IGNORECASE)]

        # Check if the position is in any protocol block
        def in_protocol_block(pos):
            return any(start <= pos < end for start, end in protocol_blocks)

        mrtdump_pattern = re.compile(r'mrtdump\s+"[^"]*"\s*;', re.IGNORECASE)
        for match in mrtdump_pattern.finditer(content):
            if not in_protocol_block(match.start()):
                # Found an existing global config of mrtdump?
                content = content[:match.start()] + new_line + content[match.end():]
                print(f"Warning: There is a existing mrt protocol configuration:\n {content}")
                break
        else:
            # Append a configuration
            content = content.strip()
            content += '\n'
            content += '\n' + new_line + '\n'

        with open(BIRD_CONF, 'w') as f:
            f.write(content)
    
    def remove_messages_mrt_config(self):
        """
        Remove the MRT config for dumping the BGP messages in the BIRD config file.
        """
        with open(BIRD_CONF, "r") as f:
            content = f.read()

        # Gather all positions of protocol {...}
        proto_spans = [
            m.span()
            for m in re.finditer(
                r'protocol\s+\w+\s*{[^}]*}',
                content,
                flags=re.IGNORECASE | re.DOTALL,
            )
        ]

        # Check if the position is in any protocol block
        def inside_protocol(pos: int) -> bool:
            return any(start <= pos < end for start, end in proto_spans)

        # Matche all lines look like mrtdump "xxx";
        mrtdump_pat = re.compile(
            r'^[ \t]*mrtdump\s+"[^"]*"\s*;\s*$', flags=re.IGNORECASE | re.MULTILINE
        )

        new_chunks = []
        last_end = 0
        removed = False

        for m in mrtdump_pat.finditer(content):
            if not inside_protocol(m.start()):
                new_chunks.append(content[last_end : m.start()])
                last_end = m.end()
                removed = True
                break

        new_chunks.append(content[last_end:])  # Append the other contents

        if removed:
            # Write back, and make sure there is a newline in the end.
            new_content = "".join(new_chunks).rstrip() + "\n"
            with open(BIRD_CONF, "w") as f:
                f.write(new_content)
    
    def config_instance(self):
        """
        Configure the BIRD router daemon instance.
        """
        os.system("sudo birdc configure")

    ########## Dump MRT file ##########

    def dump_messages(self, path: str):
        """
        Dump only BGP messages to `path`.
        """
        self.add_messages_mrt_config(path)
        self.config_instance()

    def dump_routing_table(self, path: str):
        """
        Dump the whole BGP routing table to `path`.
        """
        self.add_routes_mrt_config(path)
        self.config_instance()
    
    def stop_dump_messages(self):
        """
        Stop `dump_updates`.
        """
        self.remove_messages_mrt_config()
        self.config_instance()

    def stop_dump_routing_table(self):
        """
        Stop `dump_routing_table`.
        """
        self.remove_routes_mrt_config()
        self.config_instance()

    ########## Log manipulation ##########

    def read_log(self):
        """
        Read (all) the content from the routing softwares' log.
        Must execute with sudo-command.
        """
        return super().read_log(BIRD_LOG)

    def clear_log(self):
        """
        Clear the content from the routing softwares' log.
        Must execute with sudo-command.
        """
        super().clear_log(BIRD_LOG)
    
    ########## Crash management ##########

    # def if_crashed(self) -> bool:
    #     """
    #     Return if the router software has crashed.
    #     """
    #     output = subprocess.getoutput("systemctl is-active bird")
    #     return output!="active"
    
    @classmethod
    def if_crashed(cls) -> bool:
        """
        Return if the router software has crashed.
        """
        # Get all process
        ps_output = subprocess.check_output(["ps", "aux"]).decode("utf-8")

        # find bird
        lines = [line for line in ps_output.split("\n") 
                if "bird" in line and "grep bird" not in line and line.strip() != ""]

        # Check if there is real BIRD process
        for line in lines:
            if re.search(r"bird(\s|$|2)", line):  # match bird or bird2
                # BIRD is running.
                return False

        # BIRD is NOT running.
        return True

    def recover_from_crash(self):
        """
        Recover the software from crash.
        """
        started = not self.if_crashed()
        counter = 0
        while not started:
            os.system("sudo bird")
            sleep(0.5)
            started = not self.if_crashed()
            counter  = counter + 1
            if counter>=5:
                raise ValueError("Restarting BIRD failed for 5 times.")
    
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