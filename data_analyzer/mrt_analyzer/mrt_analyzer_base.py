from abc import abstractmethod
from ..basic_types import RouteInfo, UpdateMessageInfo
from ..utils import prefix_comp

class BaseMRTAnalyzer:
    """
    The analyzer of MRT file.
    In the essence is the interface of the MRT parsers.
    """

    @classmethod
    @abstractmethod
    def get_route_data(cls, path: str) -> list[dict]:
        """
        Return a list of dict, each represents an entry in the routing table.
        Used to analyze RIB MRT files.
        Have to deal with the repeated items in the MRT file.
        
        `path`: indicates the path to the MRT file.
        """
        raise NotImplementedError()
    
    @classmethod
    @abstractmethod
    def get_update_message_data(cls, path: str) -> list[dict]:
        """
        Return a list of dict, each represents an Update message received.
        Used to analyze message MRT files.
        
        `path`: indicates the path to the MRT file.
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def get_route_info(cls, path: str) -> list[RouteInfo]:
        """
        Return a list of RouteInfo, each represents an entry in the routing table.
        Used to analyze RIB MRT files.
        Have to deal with the repeated items in the MRT file.
        
        `path`: indicates the path to the MRT file.
        """
        raise NotImplementedError()
    
    @classmethod
    @abstractmethod
    def get_update_message_info(cls, path: str) -> list[UpdateMessageInfo]:
        """
        Return a list of UpdateMessageInfo, each represents an Update message received.
        Used to analyze message MRT files.
        
        `path`: indicates the path to the MRT file.
        """
        raise NotImplementedError()

    @classmethod
    def if_exist_route(cls, path: str, input_prefix: str) -> bool:
        """
        Check if the route to the input prefix exists.
        Used to analyze RIB MRT files.

        `path`: indicates the path to the MRT file
        """
        route_info_list: list[RouteInfo] = cls.get_route_info()
        for route_info in route_info_list:
            if prefix_comp(input_prefix, route_info.announced):
                return True
        return False
    
    @classmethod
    def if_exist_update_prefix(cls, path: str, input_prefix: str) -> bool:
        """
        Check if the UPDATE message advertising the prefix exist.
        Used to analyze message MRT files.

        `path`: indicates the path to the MRT file
        """
        update_message_info_list: list[UpdateMessageInfo] = cls.get_update_message_info()
        for update_message_info in update_message_info_list:
            for announced_prefix in update_message_info.announced:
                if prefix_comp(input_prefix, announced_prefix):
                    return True
        return False
