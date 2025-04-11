from network_utils.vnet_utils import *

import re

def parse_yaml(path):
    config = {}
    with open(path, 'r') as file:
        yaml_content = file.read()

        # Extract the key-value pair using the regex. 
        bridge_match = re.search(r"bridge:\s*(\S+)", yaml_content)
        if bridge_match:
            config["bridge"] = bridge_match.group(1)

        frr_match = re.search(r"frr:\s*\n\s*ip:\s*(\S+)\s*\n\s*veth:\s*(\S+)", yaml_content)
        if frr_match:
            config["frr"] = {
                "ip": frr_match.group(1),
                "veth": frr_match.group(2)
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

# Parse the yaml file
config = parse_yaml("vnet_config.yaml")

if __name__ == "__main__":
    print(config)
