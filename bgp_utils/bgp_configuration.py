from dataclasses import dataclass
import yaml

@dataclass
class BGP_Configuration:
    """
    You can use this class to configure the BGP instance.
    """

    ###### Basic configurations ######
    
    asn: int # AS number
    bgp_identifier: str # BGP identifier: an IPv4 address
    hold_time: int = 180 # BGP hold time
    bgp_version: int = 4 # BGP version number

    ###### BGP Options specified in Open Message ######

    route_refresh: bool = True # If use route refresh
    enhanced_route_refresh: bool = True # If use enhanced route refresh
    extended_message: bool = True # If use extended BGP message
    graceful_restart: bool = True # If use graceful restart
    mpbgp_ipv4_unicast: bool = False # If use MP-BGP IPv4 unicast.

def parse_bgp_config_from_yaml(file_path: str) -> BGP_Configuration:
    """
    Parse a YAML file and return a BGP_Configuration instance.
    
    Args:
        file_path: Path to the YAML configuration file
        
    Returns:
        BGP_Configuration instance populated from the YAML file
    """
    with open(file_path, 'r') as file:
        config_data = yaml.safe_load(file)
    
    return BGP_Configuration(
        asn=config_data['asn'],
        bgp_identifier=config_data['bgp_identifier'],
        hold_time=config_data.get('hold_time', 180),
        bgp_version=config_data.get('bgp_version', 4),
        route_refresh=config_data.get('route_refresh', True),
        enhanced_route_refresh=config_data.get('enhanced_route_refresh', True),
        extended_message=config_data.get('extended_message', True),
        graceful_restart=config_data.get('graceful_restart', True),
        mpbgp_ipv4_unicast=config_data.get('mpbgp_ipv4_unicast', True),
    )
