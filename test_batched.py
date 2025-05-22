# This file is used to test the BGP routing software in batch.
# You only need to select the test suite from `batched_testcase_factory.py` and run here.
# The routing software is automatically set-up and torn-down.

import sys, os, argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from basic_utils.binary_utils import make_bytes_displayable
from basic_utils.file_utils import *
from basic_utils.log_parse_utils import *

from test_agent.test_agent import *
from test_configuration import *
from testcase_factory.batched_testcase_factory import *

TESTCASE_ID = "id"
CRASHED_KEY = "crashed"
MESSAGE_DUMP_KEY = "message_dump"
ROUTE_DUMP_KEY = "route_dump"
PROPAGATED_KEY = "propagated"
PROPAGATE_INVALID_KEY = "propagate_invalid"

def run_test_batch(test_batch_name: str):
    """
    Run test on the test batch
    """

    ########## Configure the Router Software ##########

    router_config = RouterConfiguration(
        asn=router_software_asn,
        router_id=router_software_ip,
        neighbors=[
            Neighbor(
                peer_ip=tester_client_ip,
                peer_asn=tester_client_asn,
                local_source=router_software["veth"]
            ),
            Neighbor(
                peer_ip=exabgp_client_ip,
                peer_asn=exabgp_client_asn,
                local_source=router_software["veth"]
            ),
        ],
        router_type=router_type
    )

    ########## Initialize the TestAgent ##########

    test_agent = TestAgent(
        tcp_client_config = tcp_client_config,
        exabgp_client_config = exabgp_client_config,
    )

    ########## Run test batch ##########

    test_agent.run_test_batch(
        test_batch_name=test_batch_name,
        router_configuration=router_config
    )

def analyze_test_batch(test_batch_name: str):
    """
    Analyze the test result of the test batch.
    """
    test_batch_path = f"{TESTCASE_DUMP_BATCHED}/{test_batch_name}"
    test_batch_data_path = f"{test_batch_path}/data"
    dir_list = list_subdirectories(test_batch_data_path)
    test_info_list = []
    for dir_name in dir_list:
        dir_id = int(dir_name.split("_")[-1])
        full_path = f"{test_batch_data_path}/{dir_name}"
        test_info = {
            TESTCASE_ID: dir_id,
            CRASHED_KEY: 0, # if the software has crashed.
            MESSAGE_DUMP_KEY: 0, # if the route is dumped in the messages.
            ROUTE_DUMP_KEY: 0, # if the route is dumped in the routes.
            PROPAGATED_KEY: 0, # if the route is propagated to the next-hop.
            PROPAGATE_INVALID_KEY: 0, # if an invalid message is propagated.
        }
        if file_exists(f"{full_path}/{CRASH_MARKER_FILE}"):
            test_info[CRASHED_KEY] = 1
            test_info_list.append(test_info)
            break
        if MrtparseEngine.exist_update_prefix(f"{full_path}/{MESSAGE_MRT_FILE}",CONST_PREFIX):
            test_info[MESSAGE_DUMP_KEY] = 1
        if MrtparseEngine.exist_route(f"{full_path}/{ROUTE_MRT_FILE}",CONST_PREFIX):
            test_info[ROUTE_DUMP_KEY] = 1
        if ExaBGPLogEngine.exist_update_prefix(f"{full_path}/{EXABGP_LOG_FILE}", CONST_PREFIX):
            test_info[PROPAGATED_KEY] = 1
        if ExaBGPLogEngine.exist_invalid(f"{full_path}/{EXABGP_LOG_FILE}"):
            test_info[PROPAGATE_INVALID_KEY] = 1
        test_info_list.append(test_info)
    test_info_list = sorted(test_info_list, key=lambda x: x['id'])
    with open(f'{test_batch_path}/analysis_result.jsonl', 'w', ) as f:
        for test_info in test_info_list:
            f.write(json.dumps(test_info) + '\n')

func_name_dict = {
    "run_test_batch": run_test_batch,
    "analyze_test_batch": analyze_test_batch,
}

if __name__ == "__main__":
    # Create the arg parser. 
    parser = argparse.ArgumentParser(description="Deal with the testcase id")
    parser.add_argument(
        "--func", "-f",
        required=True,
        help="Choose the function to apply to run test batch or analyze the test results",
    )
    parser.add_argument(
        "--name", "-n",
        required=True,
        help="The name of the test batch",
    )
    args = parser.parse_args()
    
    func = args.func
    test_batch_name = args.name

    if func in func_name_dict:
        func_name_dict[func](test_batch_name)
    else:
        print(f"Invalid function name: {func}.s")
    
