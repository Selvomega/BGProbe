from basic_utils.file_utils import read_file
from .router_log_analyzer_base import BaseRouterLogAnalyzer
from ..basic_types import RouterLogInfo
from ..utils import prefix_comp, prefix_match

class BIRDRouterLogAnalyzer(BaseRouterLogAnalyzer):
    """
    The analyzer of router log file.
    """

    @classmethod
    def get_router_log_data(cls, path) -> dict:
        """
        Return a dict, representing the corresponding information in the router log.
        """
        file_content = read_file(path=path)
        withdrawn = []
        for line in file_content.splitlines():
            if "<RMT>" in line and "withdrawn" in line:
                prefix = prefix_match(line)
                if prefix_match is not None:
                    withdrawn.append(prefix)
        ret_dict = {
            "invalid": "invalid" in file_content.lower(),
            "session_break": "session closed" in file_content.lower(),
            "withdrawn": withdrawn
        }
        return ret_dict
