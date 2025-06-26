# Define the basic testcase types

from basic_utils.binary_utils import bytes2hexstr
from bgp_toolkit.message import Message

class Halt:
    """
    A dumb class used to notify the test agent to Halt.
    """
    pass

class TestCase(list[Message]):
    """
    A list of the BGP messages as the test case.
    Send one-by-one to form the test
    """
    def __new__(cls, value=None):
        if value is None:
            # Called by pickle or internal machinery, skip validation
            return super().__new__(cls)
        
        if not isinstance(value, list):
            raise ValueError("Wrong initialization of `TestCase`: value not a list")
        
        for item in value:
            if not isinstance(item, (Message, Halt)):
                raise ValueError(f"Wrong initialization of `TestCase`: {item} not a legal type")
        
        # Create the instance using the validated list
        return super().__new__(cls, value)
    
    def get_string_expression(self) -> str:
        """
        Get the string expression of the testcase.
        """
        string = ""
        for item in self:
            assert isinstance(item, (Message, Halt))
            if isinstance(item, Halt):
                string = string + "Halt\n"
            else:
                string = string + bytes2hexstr(item.get_binary_expression()) + "\n"
        return string

#################### Deprecated ####################

# class TestSuite():
#     """
#     The full description of a router software test.
#     """
#     def __init__(self,
#                  router_config: RouterConfiguration,
#                  testcases: list[TestCase],
#                  check_function: FunctionType,
#                  test_suite_name: str = None
#                  ):
#         """
#         Initialize the TestSuite.
#         `router_config`: The routing software configuration.
#         `testcases`: A list of the testcases.
#         `check_function`: Used to check if the testcase trigger the expected situation.
#         `test_suite_name`: The name of the test suite.
#         """
#         self.router_config : RouterConfiguration = router_config
#         self.testcases : list[TestCase] = testcases
#         self.check_function : FunctionType = check_function
#         self.test_suite_name : str = test_suite_name

#     def append_testcase(self, testcase: TestCase):
#         """Append a testcase to the test suite."""
#         self.testcases.append(testcase)

# @dataclass
# class TestCaseArchive:
#     """
#     The data structure used to store the necessary information to replay.
#     """
#     testcase : TestCase
#     router_config : RouterConfiguration
#     check_func : FunctionType
