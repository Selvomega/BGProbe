from .router_base import BaseRouter
from .router_frr import FRRRouter
from .basic_types import RouterSoftwareType, RouterConfiguration
import os

def collect_log_frr() -> str:
    """
    Collect the log content of the FRR instance.
    Must execute the file with sudo command.
    """
    with open("/var/log/frr/bgpd.log", 'r') as file:
        content = file.read()
    return content

def clear_log_frr():
    """
    Clear the log content of the FRR instance.
    Must execute the file with sudo command.
    """
    with open("/var/log/frr/bgpd.log", 'w') as file:
        file.write('')
    return

def get_router_interface(router_config : RouterConfiguration) -> BaseRouter:
    """
    Return the router interface according to its configuration.
    """
    router_type: RouterSoftwareType = router_config.get_router_type()
    match router_type:
        case RouterSoftwareType.FRR:
            return FRRRouter(router_config)
        case _:
            raise ValueError(f"Router type {router_type} undefined!")
