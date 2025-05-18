"""
This file defines the agent used to advertise malformed messages.
"""

from types import FunctionType
from time import sleep
from basic_utils.serialize_utils import save_variable_to_file
from basic_utils.time_utils import get_current_time
from basic_utils.file_utils import *
from basic_utils.const import *
from bgp_utils.message import MessageType
from network_utils.tcp_client import TCPClient, TCPClientConfiguration
from routing_software_interface.basic_types import RouterConfiguration, RouterSoftwareType
from routing_software_interface.router_frr import FRRRouter
from routing_software_interface.router_bird import BIRDRouter
from routing_software_interface.utils import get_router_interface
from .test_suite import Halt, TestCase, TestSuite
from .exabgp_agent import ExaBGPClient, ExaBGPClientConfiguration, start_exabgp, stop_exabgp

TEMP_DUMP_DIR = f"{REPO_ROOT_PATH}/log/temp_dump"
TEMP_MESSAGE_DUMP = f"{TEMP_DUMP_DIR}/messages.mrt"
TEMP_ROUTE_DUMP = f"{TEMP_DUMP_DIR}/routes.mrt"
TEMP_EXABGP_DUMP = f"{TEMP_DUMP_DIR}/exabgp.log"
TEMP_BGPD_DUMP = f"{TEMP_DUMP_DIR}/bgpd.log"

class TestAgent:
    """
    BGP software test agent. 
    """
    def __init__(self,
                 tcp_client_config: TCPClientConfiguration,
                 exabgp_client_config: ExaBGPClientConfiguration
                 ):
        """
        Initialize the test agent for the BGP software
        """
        # First-stage initialization
        self.tcp_client_config : TCPClientConfiguration = tcp_client_config
        self.exabgp_client_config : ExaBGPClientConfiguration = exabgp_client_config
        # Initialize the clients
        self.tcp_client = TCPClient(self.tcp_client_config)
        self.exabgp_client = ExaBGPClient(self.exabgp_client_config)
    
    def test(self):
        """For debug"""
        from test_agent.exabgp_agent import ExaBGPClient, ExaBGPClientConfiguration, start_exabgp, stop_exabgp
        from time import sleep
        ret = start_exabgp("ns-cli2")
        sleep(5)
        stop_exabgp(ret)

    # TODO: Deal with the dumping here: Can we make it a callback function?
    def run_single_testcase(self,
                            test_case: TestCase,
                            router_configuration: RouterConfiguration,
                            test_name: str):
        """
        Run a single testcase.
        """

        ########## Initialize the routing software interface. ##########

        router_interface = get_router_interface(router_configuration)

        ########## Prepare for dumping ##########

        # Create the dump directory
        test_name = f"{test_name}_{get_current_time()}"
        dump_path = f"{REPO_ROOT_PATH}/{TESTCASE_DUMP_SINGLE}/{test_name}"
        assert not directory_exists(dump_path)
        create_dir(dump_path)
        
        # Clear the bgpd log.
        router_interface.clear_log() 
        
        ########## Start the routing software instance and clients ##########

        router_interface.start_bgp_instance()
        router_interface.wait_for_log() # Start the clients one by one.
        self.exabgp_client.start()
        router_interface.wait_for_log() # Start the clients one by one.
        self.tcp_client.start()

        ########## Minor part of dumping ##########

        # Different dumping behavior for different BGP softwares
        if isinstance(router_interface, FRRRouter):
            # For FRRouting bgpd, we start to dump ONLY BGP UPDATE messages here.
            router_interface.dump_updates(f"{dump_path}/messages.mrt")
        elif isinstance(router_interface, BIRDRouter):
            # For BIRD bgpd, we start to dump ALL BGP messages here.
            router_interface.dump_messages(f"{dump_path}/messages.mrt")
        else:
            # This should not happen...
            raise ValueError("Unexpected type of the router interface!")

        ########## Send the test messages ##########

        # Send the message one-by-one
        for message in test_case:
            if isinstance(message, Halt):
                print("Halting between BGP messages to ensure fully updating...")
                sleep(2)
                continue
            self.tcp_client.send(message.get_binary_expression())
            router_interface.wait_for_log() # Wait the state to become stable.
            if router_interface.if_crashed():
                # (Currently) Save the router configuration and the testcase
                # to a special folder and restart.
                self.save_crash_setting(router_config=router_configuration,
                                        test_case=test_case)
                break
        
        ########## Main part of dumping ##########
        
        # Wait for the ExaBGP log to be ready
        sleep(2)

        # Get the contents for bgpd log and exabgp log
        bgpd_log_content = router_interface.read_log()
        exabgp_log_content = self.exabgp_client.read_log()
        # Clear the bgpd log
        # There is no need to clear the exabgp log since it will be overwritten 
        router_interface.clear_log()
        # Create bgpd log and exabgp log
        create_file(f"{dump_path}/bgpd.log", bgpd_log_content)
        create_file(f"{dump_path}/exabgp.log", exabgp_log_content)

        # Dumping RIB here, different behaviors for different BGP softwares
        if isinstance(router_interface, FRRRouter):
            # For FRRouting bgpd, dumping RIB is like taking a snapshot.
            router_interface.dump_routing_table(f"{dump_path}/routes.mrt")
            # Sleep for a while to wait for the dumping
            sleep(1.5)
        elif isinstance(router_interface, BIRDRouter):
            # For BIRD bgpd, dumping is periodic, we set the period as 1 second.
            router_interface.dump_routing_table(f"{dump_path}/routes.mrt")
            # So we need to sleep longer
            sleep(2)
        else:
            # This should not happen...
            raise ValueError("Unexpected type of the router interface!")

        # Stop MRT dumping, different behaviors for different BGP softwares
        if isinstance(router_interface, FRRRouter):
            router_interface.stop_dump_updates()
            router_interface.stop_dump_routing_table()
        elif isinstance(router_interface, BIRDRouter):
            router_interface.stop_dump_messages()
            router_interface.stop_dump_routing_table()
        else:
            # This should not happen...
            raise ValueError("Unexpected type of the router interface!")

        # Dump the testcase setting
        save_variable_to_file(router_configuration, 
                                f"{dump_path}/router_conf.pkl")
        save_variable_to_file(test_case, 
                                f"{dump_path}/test_case.pkl")
        
        # Allow user to access the dumped directory
        allow_user_access(dump_path)

        ########## End the routing software instance and clients ##########
        
        self.tcp_client.end()
        router_interface.wait_for_log() # Shut down the clients one by one.
        self.exabgp_client.end()
        router_interface.end_bgp_instance()

    
    def run_test_suite(self, 
                       test_suite: TestSuite,
                       dump_all: True):
        """
        Run the test suite, and check if the test case achieve the effect we want.
        """

        ######### Initialize the basic variables ##########

        check_func : FunctionType = test_suite.check_function
        router_configuration = test_suite.router_config
        router_interface = get_router_interface(test_suite.router_config)

        ######### Prepare the directory for dumping ##########

        dump_dir_path = f"{REPO_ROOT_PATH}/{TESTCASE_DUMP_BATCHED}/{test_suite.test_suite_name}"
        dump_path_target = f"{dump_dir_path}/target"
        dump_path_all = f"{dump_dir_path}/all"
        create_dir(dump_dir_path)
        create_dir(dump_path_target)
        create_dir(dump_path_all)

        ########## Enumerate the testcases ##########

        for test_case in test_suite.testcases:

            ###### Prepare for dumping ######

            timestamp = get_current_time()

            ###### Prepare for dumping ######

            # First clear the temporary dump files
            delete_file(TEMP_MESSAGE_DUMP)
            delete_file(TEMP_ROUTE_DUMP)
            delete_file(TEMP_EXABGP_DUMP)
            delete_file(TEMP_BGPD_DUMP)

            # Clear the bgpd log.
            router_interface.clear_log() 

            ###### Start the routing software instance and clients ######

            router_interface.start_bgp_instance()
            router_interface.wait_for_log() # Start the clients one by one.
            self.exabgp_client.start()
            router_interface.wait_for_log() # Start the clients one by one.
            self.tcp_client.start()

            ###### Minor part of dumping ######

            # We should dump into temporary path first and then 
            # copy to the "permanent storage" if `dump_all` is set.

            # Different dumping behavior for different BGP softwares
            if isinstance(router_interface, FRRRouter):
                # For FRRouting bgpd, we start to dump ONLY BGP UPDATE messages here.
                router_interface.dump_updates(TEMP_MESSAGE_DUMP)
            elif isinstance(router_interface, BIRDRouter):
                # For BIRD bgpd, we start to dump ALL BGP messages here.
                router_interface.dump_messages(TEMP_MESSAGE_DUMP)
            else:
                # This should not happen...
                raise ValueError("Unexpected type of the router interface!")

            ###### Send the test messages ######

            # Send the message one-by-one
            for message in test_case:
                if isinstance(message, Halt):
                    print("Halting between BGP messages to ensure fully updating...")
                    sleep(2)
                    continue
                self.tcp_client.send(message.get_binary_expression())
                router_interface.wait_for_log() # Wait the state to become stable.
                if router_interface.if_crashed():
                    # (Currently) Save the router configuration and the testcase
                    # to a special folder and restart.
                    self.save_crash_setting(router_config=router_configuration,
                                            test_case=test_case,
                                            name=timestamp)
                    break
            
            ###### Main part of dumping ######

            # We should dump into temporary path first and then 
            # copy to the "permanent storage" if `dump_all` is set.
        
            # Wait for the ExaBGP log to be ready
            sleep(2)

            # Get the contents for bgpd log and exabgp log
            bgpd_log_content = router_interface.read_log()
            exabgp_log_content = self.exabgp_client.read_log()
            # Clear the bgpd log
            # There is no need to clear the exabgp log since it will be overwritten 
            router_interface.clear_log()
            # Create bgpd log and exabgp log
            create_file(TEMP_BGPD_DUMP, bgpd_log_content)
            create_file(TEMP_EXABGP_DUMP, exabgp_log_content)

            # Dumping RIB here, different behaviors for different BGP softwares
            if isinstance(router_interface, FRRRouter):
                # For FRRouting bgpd, dumping RIB is like taking a snapshot.
                router_interface.dump_routing_table(TEMP_ROUTE_DUMP)
                # Sleep for a while to wait for the dumping
                sleep(1.5)
            elif isinstance(router_interface, BIRDRouter):
                # For BIRD bgpd, dumping is periodic, we set the period as 1 second.
                router_interface.dump_routing_table(TEMP_ROUTE_DUMP)
                # So we need to sleep longer
                sleep(2)
            else:
                # This should not happen...
                raise ValueError("Unexpected type of the router interface!")

            # Stop MRT dumping, different behaviors for different BGP softwares
            if isinstance(router_interface, FRRRouter):
                router_interface.stop_dump_updates()
                router_interface.stop_dump_routing_table()
            elif isinstance(router_interface, BIRDRouter):
                router_interface.stop_dump_messages()
                router_interface.stop_dump_routing_table()
            else:
                # This should not happen...
                raise ValueError("Unexpected type of the router interface!")

            ###### Dump into permatent storage if `dump_all` is set ######

            if dump_all:
                # Create the detailed dump directory
                temp_path = f"{dump_path_all}/{timestamp}"
                assert not directory_exists(temp_path)
                create_dir(temp_path)
                # Copy the temporary dumps into permanent dumps
                if file_exists(TEMP_MESSAGE_DUMP):
                    os.system(f"sudo cp {TEMP_MESSAGE_DUMP} {temp_path}/messages.mrt")
                if file_exists(TEMP_ROUTE_DUMP):
                    os.system(f"sudo cp {TEMP_ROUTE_DUMP} {temp_path}/routes.mrt")
                if file_exists(TEMP_EXABGP_DUMP):
                    os.system(f"sudo cp {TEMP_EXABGP_DUMP} {temp_path}/exabgp.log")
                if file_exists(TEMP_BGPD_DUMP):
                    os.system(f"sudo cp {TEMP_BGPD_DUMP} {temp_path}/bgpd.log")
                # Dump the testcase setting
                save_variable_to_file(router_configuration, 
                                      f"{temp_path}/router_conf.pkl")
                save_variable_to_file(test_case,
                                      f"{temp_path}/test_case.pkl")

            ###### Check if the testcase satisfies expectation ######

            if check_func():
                # Condition satisfied, save to the target directory
                temp_path = f"{dump_path_target}/{timestamp}"
                assert not directory_exists(temp_path)
                create_dir(temp_path)
                # Copy the temporary dumps into permanent dumps
                if file_exists(TEMP_MESSAGE_DUMP):
                    os.system(f"sudo cp {TEMP_MESSAGE_DUMP} {temp_path}/messages.mrt")
                if file_exists(TEMP_ROUTE_DUMP):
                    os.system(f"sudo cp {TEMP_ROUTE_DUMP} {temp_path}/routes.mrt")
                if file_exists(TEMP_EXABGP_DUMP):
                    os.system(f"sudo cp {TEMP_EXABGP_DUMP} {temp_path}/exabgp.log")
                if file_exists(TEMP_BGPD_DUMP):
                    os.system(f"sudo cp {TEMP_BGPD_DUMP} {temp_path}/bgpd.log")
                # Dump the testcase setting
                save_variable_to_file(router_configuration, 
                                      f"{temp_path}/router_conf.pkl")
                save_variable_to_file(test_case,
                                      f"{temp_path}/test_case.pkl")
                
            ###### Recover if the routing software crashes ######

            if router_interface.if_crashed():
                router_interface.recover_from_crash()

            ###### End the routing software instance and clients ######
            
            self.tcp_client.end()
            router_interface.wait_for_log() # Shut down the clients one by one.
            self.exabgp_client.end()
            router_interface.end_bgp_instance()

    def save_crash_setting(self,
                           router_config: RouterConfiguration,
                           test_case: TestCase,
                           name: str = None):
        """
        Save the test setting causing crash.
        """
        if name is None:
            name = get_current_time()
        crash_dump_path = f"{REPO_ROOT_PATH}/{TESTCASE_DUMP_CRASHED}"
        dump_path = f"{crash_dump_path}/{name}"
        assert not directory_exists(dump_path)
        create_dir(dump_path)
        save_variable_to_file(router_config,
                              f"{dump_path}/router_config.pkl")
        save_variable_to_file(test_case,
                              f"{dump_path}/testcase.pkl")
