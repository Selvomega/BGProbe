# This file is used to test the BGP routing software iteratively.
# You only need to select the testcase from `testcase_factory.py` and run here.
# The routing software is automatically set-up and torn-down.

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from test_agent.test_agent import TestAgent

from test_configuration import *
from testcase_factory import testcase_1, testcase_2

########## Initialize the TestAgent ##########

test_agent = TestAgent(
    tcp_client_config = tcp_client_config,
)

########## Run testcase ##########

testcase = testcase_2

test_agent.run_single_testcase(
    test_case=testcase,
    router_configuration=router_config,
)

########## Debug testcase ##########

# update_msg = testcase[-1]
# print(make_bytes_displayable(update_msg.get_binary_expression()))
