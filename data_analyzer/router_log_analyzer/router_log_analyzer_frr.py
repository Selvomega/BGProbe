from basic_utils.file_utils import read_file
from .router_log_analyzer_base import BaseRouterLogAnalyzer
from ..utils import prefix_comp, prefix_match

class FRRRouterLogAnalyzer(BaseRouterLogAnalyzer):
    """
    The analyzer of router log file.
    """

    @classmethod
    def route_withdrawn(cls, path: str, route: str) -> bool:
        """
        Check if the given route is withdrawn by the router.
        """
        file_content = read_file(path=path)
        # TODO

    @classmethod
    def session_break(cls, path: str) -> bool:
        """
        Check if session break happens in the router.
        """
        file_content = read_file(path=path)
        # TODO
    
    @classmethod
    def check_invalid(cls, path: str) -> bool:
        """
        Check if the router has received an invalid message.
        """
        file_content = read_file(path=path)
        # TODO
