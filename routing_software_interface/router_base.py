"""
The basic type of the router. 
"""

from abc import ABC, abstractmethod
from .basic_types import *

class BaseRouter(ABC):
    """
    The base type of the router. 
    """
    @abstractmethod
    def __init__(self, configuration : RouterConfiguration):
        """
        Initialize the BGP router. 
        """
        self.software_type : RouterSoftwareType = None
        self.router_configuration : RouterConfiguration = configuration
    
    @abstractmethod
    def start_bgp_instance(self):
        """
        Start the BGP instance using `self.router_configuration` 
        """
        raise NotImplementedError("`start_bgp_instance` not implemented!")

    @abstractmethod
    def end_bgp_instance(self):
        """
        Shut down the BGP instance
        """
        raise NotImplementedError("`end_bgp_instance` not implemented!")

    @abstractmethod
    def restart_bgp_instance(self):
        """
        Restart the BGP instance.
        """
        raise NotImplementedError("`restart_bgp_instance` not implemented!")

    @abstractmethod
    def append_local_prefix(self, prefix: str):
        """
        Add a local prefix to the router.
        The base class will append the prefix to the configuration.
        You should call `super().append_local_prefix(prefix)`.
        """
        return self.router_configuration.append_local_prefix(prefix)

    @abstractmethod
    def remove_local_prefix(self, prefix: str):
        """
        Reove a local prefix to the router.
        The base class will remove the prefix to the configuration.
        You should call `super().remove_local_prefix(prefix)`.
        """
        return self.router_configuration.remove_local_prefix(prefix)

    @abstractmethod
    def append_neighbor(self, neighbor: Neighbor):
        """
        Add a neighbor to the router.
        The base class will append the prefix to the configuration.
        You should call `super().append_neighbor(neighbor)`.
        """
        return self.router_configuration.append_neighbor(neighbor)

    @abstractmethod
    def remove_neighbor(self, neighbor: Neighbor):
        """
        Reove a neighbor from the router.
        The base class will remove the prefix to the configuration.
        You should call `super().remove_neighbor(neighbor)`.
        """
        return self.router_configuration.remove_neighbor(neighbor)

    def get_software_type(self):
        """
        Get the type of the software
        """
        return self.software_type

    def get_router_configuration(self):
        """
        Get the configuration of the router
        """
        return self.router_configuration
