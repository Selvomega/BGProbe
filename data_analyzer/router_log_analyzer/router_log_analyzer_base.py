from abc import abstractmethod
from ..basic_types import RouterLogInfo
from ..utils import prefix_comp

class BaseRouterLogAnalyzer:
    """
    The analyzer of router log file.
    """

    @classmethod
    @abstractmethod
    def get_router_log_data(cls, path: str) -> dict:
        """
        Return a dict representing the corresponding information in the router log.
        """
        raise NotImplementedError()

    @classmethod
    def get_router_log_info(cls, path: str) -> RouterLogInfo:
        """
        Return a RouterLogInfo, representing the corresponding information in the router log.
        """
        router_log_dict = cls.get_router_log_data(path)
        return RouterLogInfo(
            invalid = router_log_dict["invalid"],
            session_break = router_log_dict["session_break"],
            withdrawn = router_log_dict["withdrawn"],
        )

    @classmethod
    def if_route_withdrawn(cls, path: str, route: str) -> bool:
        """
        Check if the given route is withdrawn by the router.
        """
        router_log_info : RouterLogInfo = cls.get_router_log_info()
        for wroute in router_log_info.withdrawn:
            if prefix_comp(route, wroute):
                return True
        return False

    @classmethod
    def if_session_break(cls, path: str) -> bool:
        """
        Check if session break happens in the router.
        """
        router_log_info : RouterLogInfo = cls.get_router_log_info()
        return router_log_info.session_break
    
    @classmethod
    def if_invalid(cls, path: str) -> bool:
        """
        Check if the router has received an invalid message.
        """
        router_log_info : RouterLogInfo = cls.get_router_log_info()
        return router_log_info.invalid
