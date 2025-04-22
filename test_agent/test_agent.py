"""
This file defines the agent used by the test.
"""

from types import FunctionType
from data_utils.serialize_utils import save_variable_to_file
from bgp_utils_update.message import MessageType
from network_utils.tcp_client import TCPClient, TCPClientConfiguration
from routing_software_interface.basic_types import RouterConfiguration, RouterSoftwareType
from routing_software_interface.router_frr import FRRRouter
from .test_suite import TestSuite, TestCaseArchive

class TestAgent:
    """
    BGP software test agent. 
    """
    def __init__(self,
                 # bgp_client_config: BGPClientConfiguration,
                 tcp_client_config: TCPClientConfiguration,
                 router_config: RouterConfiguration,
                 router_type: RouterSoftwareType,
                 test_suite: TestSuite,
                 check_func: FunctionType,
                 dump_path: str
                 ):
        """
        Initialize the test agent for the BGP software
        """
        
        # First-stage initialization
        # self.bgp_client_config : BGPClientConfiguration = bgp_client_config
        self.tcp_client_config : TCPClientConfiguration = tcp_client_config
        self.router_config : RouterConfiguration = router_config
        self.router_type : RouterSoftwareType = router_type
        self.test_suite : TestSuite = test_suite
        self.check_func : FunctionType = check_func
        self.dump_path : str = dump_path

        # Initialize the clients
        self.tcp_client = TCPClient(self.tcp_client_config)
        match self.router_type:
            case RouterSoftwareType.FRR:
                self.router_interface = FRRRouter(self.router_config)
            case _:
                raise ValueError(f"Router type {router_type} undefined!")
    
    def run_test_suite(self):
        """
        Run the test suite, and check if the test case achieve the effect we want.
        """
        for testcase in self.test_suite:
            # First start the routing software and the TCP client.
            self.router_interface.start_bgp_instance()
            self.tcp_client.start()

            # Send the message one-by-one
            for message in testcase:
                self.tcp_client.send(message.get_binary_expression())
                if message.get_message_type() in [MessageType.OPEN, MessageType.KEEPALIVE]:
                    # Receive the exchanged message for 
                    received = self.tcp_client.receive()
                # TODO: deal with connection ending here
                if self.check_func():
                    # if the testcase is satisfying
                    testcase_archive = TestCaseArchive(testcase=testcase,
                                                       router_config=self.router_config,
                                                       check_func=self.check_func)
                    # Dump the testcase_archive to the storage. 
                    save_variable_to_file(testcase_archive,self.dump_path)
                    break

            # End of iteration, shut down the routing software and the TCP client.
            from time import sleep
            sleep(10)
            self.router_interface.end_bgp_instance()
            self.tcp_client.end()
