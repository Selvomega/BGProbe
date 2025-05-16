# This file is used to test the BGP routing software iteratively.
# You only need to select the testcase from `testcase_factory.py` and run here.
# The routing software is automatically set-up and torn-down.

import sys, os, argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from basic_utils.binary_utils import make_bytes_displayable
from routing_software_interface.basic_types import RouterSoftwareType

from test_agent.test_agent import TestAgent
from test_configuration import *
from testcase_factory import testcase_suite

router_type = RouterSoftwareType.BIRD

def main(test_id: int):
    """
    The main function of running the test cases.
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

    ########## Load the Testcase ##########

    testcase = testcase_suite[test_id]

    ########## Initialize the TestAgent ##########

    test_agent = TestAgent(
        tcp_client_config = tcp_client_config,
        exabgp_client_config = exabgp_client_config,
    )

    ########## Run testcase ##########

    test_agent.run_single_testcase(
        test_case=testcase,
        router_configuration=router_config,
        test_name=f"testcase-{test_id}",
    )

    ########## Debug testcase ##########

    # update_msg = testcase[-1]
    # print(make_bytes_displayable(update_msg.get_binary_expression()))


if __name__ == "__main__":
    # Create the arg parser. 
    parser = argparse.ArgumentParser(description="Deal with the testcase id")
    parser.add_argument(
        "number", 
        type=int, 
        help=f"Please enter an integer between 1-{len(testcase_suite)-1}",
        choices=range(1, len(testcase_suite))  # 限制范围1-30
    )
    args = parser.parse_args()
    # Run the main function. 
    main(test_id=args.number)
    