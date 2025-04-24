"""
This file defines the agent used by the test.
"""

from types import FunctionType
from basic_utils.serialize_utils import save_variable_to_file
from basic_utils.time_utils import get_current_time
from basic_utils.file_utils import *
from bgp_utils.message import MessageType
from network_utils.tcp_client import TCPClient, TCPClientConfiguration
from routing_software_interface.basic_types import RouterConfiguration, RouterSoftwareType
from routing_software_interface.router_frr import FRRRouter
from routing_software_interface.utils import get_router_interface
from .test_suite import TestCase, TestSuite, TestCaseArchive

class TestAgent:
    """
    BGP software test agent. 
    """
    def __init__(self,
                 tcp_client_config: TCPClientConfiguration,
                 ):
        """
        Initialize the test agent for the BGP software
        """
        # First-stage initialization
        self.tcp_client_config : TCPClientConfiguration = tcp_client_config
        # Initialize the clients
        self.tcp_client = TCPClient(self.tcp_client_config)

    def run_single_testcase(self,
                            test_case: TestCase,
                            router_configuration: RouterConfiguration,
                            dump: bool = True):
        """
        Run a single testcase.
        """
        # Start the routing software and the TCP client.
        router_interface = get_router_interface(router_configuration)
        router_interface.clear_log() # First clear the log.
        router_interface.start_bgp_instance()
        self.tcp_client.start()

        # Send the message one-by-one
        for message in test_case:
            self.tcp_client.send(message.get_binary_expression())
            # TODO: Deal with connection ending and crashes here.
            if message.get_message_type() in [MessageType.OPEN, MessageType.KEEPALIVE]:
                # Receive the exchanged OPEN and KEEPALIVE message 
                # to make the messages chronological
                received = self.tcp_client.receive()
        
        from time import sleep
        sleep(2)

        if dump:
            log_content = router_interface.read_log()
            router_interface.clear_log()
            time_str = get_current_time()
            dump_dir_path = f"{get_repo_root()}/{TESTCASE_DUMP_SINGLE}/{time_str}"
            assert not directory_exists(dump_dir_path)
            create_dir(dump_dir_path)
            create_file(f"{dump_dir_path}/bgpd.log", log_content)
            save_variable_to_file(router_configuration, 
                                  f"{dump_dir_path}/router_conf.pkl")
            save_variable_to_file(test_case, 
                                  f"{dump_dir_path}/test_case.pkl")
        
        self.tcp_client.end()
        router_interface.end_bgp_instance()

    
    def run_test_suite(self, 
                       test_suite: TestSuite,):
        """
        Run the test suite, and check if the test case achieve the effect we want.
        """

        ###### Initialize the basic variables ######

        check_func : FunctionType = test_suite.check_function
        router_config : RouterConfiguration = test_suite.router_config
        router_interface = get_router_interface(router_config)

        ###### Prepare for variable dumping ######

        test_name : str = test_suite.test_suite_name
        test_name = get_current_time() if test_name is None else test_name
        dump_dir_path = f"{get_repo_root()}/{TESTCASE_DUMP_BATCHED}/{test_name}"
        assert not directory_exists(dump_dir_path)
        create_dir(dump_dir_path)
        save_variable_to_file(check_func,
                              f"{dump_dir_path}/check_func.pkl")
        save_variable_to_file(router_config,
                              f"{dump_dir_path}/router_conf.pkl")
        for testcase in test_suite.testcases:
            save_variable_to_file(testcase,
                                  f"{dump_dir_path}/original_testcases.pkl")

        ###### Run test ######

        for testcase in test_suite.testcases:
            # First clear the log of the routing software.
            router_interface.clear_log()
            # First start the routing software and the TCP client.
            router_interface.start_bgp_instance()
            self.tcp_client.start()

            # Send the message one-by-one
            for message in testcase:
                self.tcp_client.send(message.get_binary_expression())
                # TODO: Deal with connection ending and crashes here.
                if message.get_message_type() in [MessageType.OPEN, MessageType.KEEPALIVE]:
                    # Receive the exchanged OPEN and KEEPALIVE message 
                    # to make the messages chronological
                    received = self.tcp_client.receive()
                if check_func():
                    # Dump the testcase_archive to the storage. 
                    save_variable_to_file(testcase,
                                          f"{dump_dir_path}/passed_testcases.pkl")
                    break

            # End of iteration, shut down the routing software and the TCP client.
            from time import sleep
            sleep(10)

            # Shut down the routing software and the TCP client.
            self.tcp_client.end()
            router_interface.end_bgp_instance()
