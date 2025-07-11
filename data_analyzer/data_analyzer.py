from .basic_types import *
from .exabgp_log_analyzer import ExaBGPLogAnalyzer
from .mrt_analyzer import BaseMRTAnalyzer, BGPdumpMRTAnalyzer, MRTParseMRTAnalyzer
from .router_log_analyzer import BaseRouterLogAnalyzer, BIRDRouterLogAnalyzer, FRRRouterLogAnalyzer
from run.testbed import MESSAGE_MRT_FILE, ROUTE_MRT_FILE, EXABGP_LOG_FILE, BGPD_LOG_FILE
from bgprobe_config import router_type
from test_agents.router_agent import RouterAgentType
from basic_utils.file_utils import delete_file, ANALYZED_DUMP, natural_key
import os, json

class DataAnalyzer:
    """
    The class used to analyze the data dumped in BGProbe pipeline.

    Functionalities:
    1. Synthesize the information of the testcases using the analyzers
    2. Store/Read the synthesized information to/from local files
    3. Compare the synthesized information from different implementations
    """
    
    @classmethod
    def generate_testcase_report(cls, path: str, testcase_id: str) -> dict:
        """
        Generate the testcase report from the data dumped.

        Use `MRTParseMRTAnalyzer` as the MRT parser
        """
        route_mrt_path = f"{path}/{ROUTE_MRT_FILE}"
        message_mrt_path = f"{path}/{MESSAGE_MRT_FILE}"
        router_log_path = f"{path}/{BGPD_LOG_FILE}"
        exabgp_log_path = f"{path}/{EXABGP_LOG_FILE}"

        match router_type:
            case RouterAgentType.FRR:
                router_log_data = FRRRouterLogAnalyzer.get_router_log_data(router_log_path)
            case RouterAgentType.BIRD:
                router_log_data = BIRDRouterLogAnalyzer.get_router_log_data(router_log_path)
            case _:
                raise ValueError("Unrecognized router type!")

        ret_report : TestcaseReport = {
           "testcase_id": testcase_id,
           "mrt_route_data": MRTParseMRTAnalyzer.get_route_data(route_mrt_path),
           "mrt_update_message_data": MRTParseMRTAnalyzer.get_update_message_data(message_mrt_path),
           "router_log_data": router_log_data,
           "exabgp_log_data": ExaBGPLogAnalyzer.get_exabgp_log_data(exabgp_log_path)
        }
        return ret_report
    
        # return TestcaseReport(
        #     testcase_id = testcase_id,
        #     mrt_route_data = MRTParseMRTAnalyzer.get_route_data(route_mrt_path),
        #     mrt_update_message_data = MRTParseMRTAnalyzer.get_update_message_data(message_mrt_path),
        #     router_log_data = router_log_data,
        #     exabgp_log_data= ExaBGPLogAnalyzer.get_exabgp_log_data(exabgp_log_path)
        # )
    
    @classmethod
    def generate_batched_report(cls, path: str, batch_name: str) -> list:
        """
        Generate a batch of testcase reports.

        The batch are stored under the directory indicated by `path`.
        """
        ret_list = []
        testcase_dir_list = sorted(os.listdir(path), key=natural_key)
        for testcase_dir in testcase_dir_list:
            new_path = f"{path}/{testcase_dir}"
            testcase_id = f"{batch_name}_{testcase_dir}"
            cur_report = cls.generate_testcase_report(new_path, testcase_id)
            ret_list.append(cur_report)
        return ret_list

    @classmethod
    def dump_batched_report(cls, path: str, batch_name: str, dump_path: str = ANALYZED_DUMP):
        """
        Generate and dump a batch of testcase reports.

        The batch are stored under the directory indicated by `path`.
        `batch_name` and the file name MUST match.
        """
        dump_file_path = f"{dump_path}/{batch_name}.jsonl"
        # Over-write the report
        delete_file(dump_file_path)

        batched_reports = cls.generate_batched_report(path, batch_name)
        with open(dump_file_path, "a") as f:
            for report in batched_reports:
                f.write(json.dumps(report) + "\n")

    @classmethod
    def read_batched_report(cls, path: str):
        """
        Read the batched report out.
        """
        ret_list: list[TestcaseReport] = []
        with open(path, "r") as f:
            for line in f:
                report: TestcaseReport = json.loads(line)
                ret_list.append(report)
        return ret_list
