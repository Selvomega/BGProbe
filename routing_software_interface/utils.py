from .router_base import BaseRouter
from .router_frr import FRRRouter
from .router_bird import BIRDRouter
from .basic_types import RouterSoftwareType, RouterConfiguration
import os

def get_router_interface(router_config : RouterConfiguration) -> BaseRouter:
    """
    Return the router interface according to its configuration.
    """
    router_type: RouterSoftwareType = router_config.get_router_type()
    match router_type:
        case RouterSoftwareType.FRR:
            return FRRRouter(router_config)
        case RouterSoftwareType.BIRD:
            return BIRDRouter(router_config)
        case _:
            raise ValueError(f"Router type {router_type} undefined!")
