"""
This file defines the agent used to advertise malformed messages.
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
            router_interface.wait_for_log() # Wait the state to become stable.
            if router_interface.if_crashed():
                # (Currently) Save the router configuration and the testcase
                # to a special folder and restart.
                self.save_crash_setting(router_config=router_configuration,
                                        test_case=test_case)
                break

        if dump:
            log_content = router_interface.read_log()
            router_interface.clear_log()
            time_str = get_current_time()
            dump_path = f"{get_repo_root()}/{TESTCASE_DUMP_SINGLE}/{time_str}"
            assert not directory_exists(dump_path)
            create_dir(dump_path)
            create_file(f"{dump_path}/bgpd.log", log_content)
            save_variable_to_file(router_configuration, 
                                  f"{dump_path}/router_conf.pkl")
            save_variable_to_file(test_case, 
                                  f"{dump_path}/test_case.pkl")
        
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
        for test_case in test_suite.testcases:
            save_variable_to_file(test_case,
                                  f"{dump_dir_path}/original_testcases.pkl")

        ###### Run test ######

        for test_case in test_suite.testcases:
            # First clear the log of the routing software.
            router_interface.clear_log()
            # First start the routing software and the TCP client.
            router_interface.start_bgp_instance()
            self.tcp_client.start()

            # Send the message one-by-one
            for message in test_case:
                self.tcp_client.send(message.get_binary_expression())
                router_interface.wait_for_log() # Wait the state to become stable.
                if router_interface.if_crashed():
                    # (Currently) Save the router configuration and the testcase
                    # to a special folder and restart.
                    self.save_crash_setting(router_config=router_config,
                                            test_case=test_case)
                    break
                if check_func():
                    # Dump the testcase_archive to the storage. 
                    save_variable_to_file(test_case,
                                          f"{dump_dir_path}/passed_testcases.pkl")
                    break

            # Shut down the routing software and the TCP client.
            self.tcp_client.end()
            router_interface.end_bgp_instance()

    def save_crash_setting(self,
                           router_config: RouterConfiguration,
                           test_case: TestCase):
        """
        Save the test setting causing crash.
        """
        time_str = get_current_time()
        crash_dump_path = f"{get_repo_root()}/{TESTCASE_DUMP_CRASHED}"
        save_variable_to_file(router_config,
                              f"{crash_dump_path}/{time_str}.pkl")
        save_variable_to_file(test_case,
                              f"{crash_dump_path}/{time_str}.pkl")
