"""
This class defines the test cases.
"""

from dataclasses import dataclass
from types import FunctionType
from bgp_utils.message import Message
from routing_software_interface.basic_types import RouterConfiguration

class TestCase(list[Message]):
    """
    A list of the BGP messages as the test case.
    Send one-by-one to form the test
    """
    def __new__(cls, value):
        if not isinstance(value, list):
            raise ValueError("Wrong initialization of `TestCase`: value not a list")
        ret_list  = []
        for item in value:
            if not isinstance(item, Message):
                raise ValueError(f"Wrong initialization of `TestCase`: {item} not a legal type")
            ret_list.append(item)
        return super().__new__(cls, ret_list)

class TestSuite():
    """
    The full description of a router software test.
    """
    def __init__(self,
                 router_config: RouterConfiguration,
                 testcases: list[TestCase],
                 check_function: FunctionType,
                 test_suite_name: str = None
                 ):
        """
        Initialize the TestSuite.
        `router_config`: The routing software configuration.
        `testcases`: A list of the testcases.
        `check_function`: Used to check if the testcase trigger the expected situation.
        `test_suite_name`: The name of the test suite.
        """
        self.router_config : RouterConfiguration = router_config
        self.testcases : list[TestCase] = testcases
        self.check_function : FunctionType = check_function
        self.test_suite_name : str = test_suite_name

    def append_testcase(self, testcase: TestCase):
        """Append a testcase to the test suite."""
        self.testcases.append(testcase)

@dataclass
class TestCaseArchive:
    """
    The data structure used to store the necessary information to replay.
    """
    testcase : TestCase
    router_config : RouterConfiguration
    check_func : FunctionType
