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

class TestSuite(list[TestCase]):
    """
    A list of the test cases as the test suite.
    """
    def __new__(cls, value):
        if not isinstance(value, list):
            raise ValueError("Wrong initialization of `TestSuite`: value not a list")
        ret_list  = []
        for item in value:
            if not isinstance(item, TestCase):
                raise ValueError(f"Wrong initialization of `TestSuite`: {item} not a legal type")
            ret_list.append(item)
        return super().__new__(cls, ret_list)

@dataclass
class TestCaseArchive:
    """
    The data structure used to store the necessary information to replay.
    """
    testcase : TestCase
    router_config : RouterConfiguration
    check_func : FunctionType
    log : str = "" # The log after test
