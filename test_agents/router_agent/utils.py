from .router_agent_base import BaseRouterAgent
from .router_agent_frr import FRRRouterAgent
from .router_agent_bird import BIRDRouterAgent
from .router_agent_gobgp import GoBGPRouterAgent
from .basic_types import RouterAgentType, RouterAgentConfiguration

def get_router_agent(router_agent_config : RouterAgentConfiguration) -> BaseRouterAgent:
    """
    Return the router interface according to its configuration.
    """
    router_type: RouterAgentType = router_agent_config.get_router_type()
    match router_type:
        case RouterAgentType.FRR:
            return FRRRouterAgent(router_agent_config)
        case RouterAgentType.BIRD:
            return BIRDRouterAgent(router_agent_config)
        case RouterAgentType.GOBGP:
            return GoBGPRouterAgent(router_agent_config)
        case _:
            raise ValueError(f"Router type {router_type} undefined!")
