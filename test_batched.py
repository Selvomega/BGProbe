# This file is used to test the BGP routing software in batch.
# You only need to select the test suite from `testsuite_factory.py` and run here.
# The routing software is automatically set-up and torn-down.

import sys, os, argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from basic_utils.binary_utils import make_bytes_displayable

from test_agent.test_agent import TestAgent
from test_configuration import *
from testsuite_factory import test_suite_list

def main(test_id: int, dump_all: bool):
    """
    The main function of running the test cases.
    """

    ########## Load the Test Suite ##########

    test_suite = test_suite_list[test_id]

    ########## Initialize the TestAgent ##########

    test_agent = TestAgent(
        tcp_client_config = tcp_client_config,
        exabgp_client_config = exabgp_client_config,
    )

    ########## Run test suite ##########

    test_agent.run_test_suite(
        test_suite=test_suite,
        dump_all=dump_all,
    )

    ########## Debug test suite ##########

    # TODO


if __name__ == "__main__":
    # Create the arg parser. 
    parser = argparse.ArgumentParser(description="Deal with the testcase id")
    parser.add_argument(
        "number", 
        type=int, 
        help=f"Please enter an integer between 0-{len(test_suite_list)-1}",
        choices=range(0, len(test_suite_list)),
    )
    parser.add_argument(
        "--dumpall", 
        action="store_true",
        help="If we should dump all testcases",
        default=False,
    )
    args = parser.parse_args()
    # Run the main function. 
    main(test_id=args.number, dump_all=args.dumpall)
