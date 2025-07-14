"""
The basic type of the router agent. 
"""

from abc import ABC, abstractmethod
from time import sleep
from .basic_types import *

class BaseRouterAgent(ABC):
    """
    The base type of the router. 
    """

    ########## Initialization ##########

    @abstractmethod
    def __init__(self, configuration : RouterAgentConfiguration):
        """
        Initialize the BGP router. 
        """
        self.router_agent_type : RouterAgentType = None
        self.router_agent_configuration : RouterAgentConfiguration = configuration

    ########## Turn on/off the instance ##########

    @abstractmethod
    def start_bgp_instance(self):
        """
        Start the BGP instance using `self.router_agent_configuration` 
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

    ########## Get methods ##########

    def get_software_type(self):
        """
        Get the software type of the router agent.
        """
        return self.software_type

    def get_configuration(self):
        """
        Get the configuration of the router agent.
        """
        return self.router_configuration

    ########## Log manipulation ##########

    @abstractmethod
    def read_log(self):
        """
        Read (all) the content from the routing softwares' log.
        Must execute with sudo-command.
        """
        raise NotImplementedError("`restart_bgp_instance` not implemented!")

    @abstractmethod
    def clear_log(self, path: str):
        """
        Clear the content from the routing softwares' log.
        Must execute with sudo-command.
        """
        raise NotImplementedError("`restart_bgp_instance` not implemented!")

    ########## Crash management ##########

    @classmethod
    @abstractmethod
    def if_crashed(cls) -> bool:
        """
        Return if the router software has crashed.
        """
        raise NotImplementedError()

    @abstractmethod
    def recover_from_crash(self):
        """
        Recover the software from crash.
        """
        raise NotImplementedError()

    @abstractmethod
    def restart_software(self):
        """
        Restart the software.
        """
        raise NotImplementedError()

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
            sleep(time_duration)
