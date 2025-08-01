# This file is used to test the BGP routing software iteratively.
# You only need to select the testcase from `single_testcase_factory.py` and run here.
# The routing software is automatically set-up and torn-down.

import sys, os, argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from basic_utils.binary_utils import make_bytes_displayable

from test_agents.router_agent import *

from bgprobe_config import *
from testcase_factory.single_testcase_factory import single_testcase_suite

from testbed import *

def main(test_name: str = None):
    """
    The main function of running single testcases.
    """

    ########## Configure the Router Software ##########

    router_agent_config = RouterAgentConfiguration(
        asn=router_agent_asn,
        router_id=router_agent_ip,
        neighbors=[
            Neighbor(
                peer_ip=tester_agent_ip,
                peer_asn=tester_agent_asn,
                local_source=router_agent["veth"]
            ),
            Neighbor(
                peer_ip=exabgp_agent_ip,
                peer_asn=exabgp_agent_asn,
                local_source=router_agent["veth"]
            ),
        ],
        router_type=router_type
    )

    ########## Initialize the Testbed ##########

    testbed = Testbed(
        tcp_agent_config = tcp_agent_config,
        router_agent_config = router_agent_config,
        exabgp_agent_config = exabgp_agent_config,
    )

    ########## Run all single testcases ##########

    if test_name is None:
        test_name = "all_single_testcases"

    testbed.run_test_single_all(
        test_name = test_name,
    )

if __name__ == "__main__":
    # Create the arg parser. 
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--test_name",
        type=str,
        default=None,
        help="Optional name for the test",
    )
    args = parser.parse_args()
    # Run the main function. 
    main(test_name=args.test_name)
