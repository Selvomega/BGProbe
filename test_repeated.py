# This file is used to test the BGP routing software iteratively.
# You only need to select the testcase from `single_testcase_factory.py` and run here.
# The routing software is automatically set-up and torn-down.

import sys, os, argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from basic_utils.binary_utils import make_bytes_displayable

from test_agent.test_agent import TestAgent
from test_configuration import *
from testcase_factory.repeated_testcase_factory import repeated_testcase_suite

def main(test_id: int, repeat_num: int):
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

    testcase, testcase_name = repeated_testcase_suite[test_id]

    ########## Initialize the TestAgent ##########

    test_agent = TestAgent(
        tcp_client_config = tcp_client_config,
        exabgp_client_config = exabgp_client_config,
    )

    ########## Run testcase ##########

    test_agent.run_test_repeated(
        testcase_name=testcase_name,
        test_case=testcase,
        router_configuration=router_config,
        repeated_num=repeat_num,
    )

    ########## Debug testcase ##########

    # update_msg = testcase[-1]
    # print(make_bytes_displayable(update_msg.get_binary_expression()))


if __name__ == "__main__":
    # Create the arg parser. 
    def non_negative_int(value):
        ivalue = int(value)
        if ivalue < 0:
            raise argparse.ArgumentTypeError(f"{value} is an invalid non-negative int value")
        return ivalue
    parser = argparse.ArgumentParser(description="Deal with the testcase id")
    parser.add_argument(
        "--number", "-n",
        type=int, 
        help=f"Please enter an integer between 0-{len(repeated_testcase_suite)-1}",
        choices=range(0, len(repeated_testcase_suite))
    )
    parser.add_argument(
        "--repeat", "-r",
        type=non_negative_int, 
        help=f"Please enter the number of times you want to repeat the execution.",
    )
    args = parser.parse_args()
    # Run the main function. 
    main(test_id=args.number, repeat_num=args.repeat)
