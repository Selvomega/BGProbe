"""
This file defines the agent used to advertise malformed messages.
"""

from types import FunctionType
from time import sleep
from basic_utils.serialize_utils import save_variable_to_file, read_variables_from_file
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

MESSAGE_MRT_FILE = "messages.mrt"
ROUTE_MRT_FILE = "routes.mrt"
EXABGP_LOG_FILE = "exabgp.log"
BGPD_LOG_FILE = "bgpd.log"
ROUTER_CONFIG_PKL_FILE = "router_conf.pkl"
TESTCASE_PKL_FILE = "testcase.pkl"
CRASH_MARKER_FILE = "crashed"

TEMP_DUMP_DIR = f"{REPO_ROOT_PATH}/log/temp_dump"
TEMP_MESSAGE_DUMP = f"{TEMP_DUMP_DIR}/{MESSAGE_MRT_FILE}"
TEMP_ROUTE_DUMP = f"{TEMP_DUMP_DIR}/{ROUTE_MRT_FILE}"
TEMP_EXABGP_DUMP = f"{TEMP_DUMP_DIR}/{EXABGP_LOG_FILE}"
TEMP_BGPD_DUMP = f"{TEMP_DUMP_DIR}/{BGPD_LOG_FILE}"

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
    def run_test_single(self,
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
            router_interface.dump_updates(f"{dump_path}/{MESSAGE_MRT_FILE}")
        elif isinstance(router_interface, BIRDRouter):
            # For BIRD bgpd, we start to dump ALL BGP messages here.
            router_interface.dump_messages(f"{dump_path}/{MESSAGE_MRT_FILE}")
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
        create_file(f"{dump_path}/{BGPD_LOG_FILE}", bgpd_log_content)
        create_file(f"{dump_path}/{EXABGP_LOG_FILE}", exabgp_log_content)

        # Dumping RIB here, different behaviors for different BGP softwares
        if isinstance(router_interface, FRRRouter):
            # For FRRouting bgpd, dumping RIB is like taking a snapshot.
            router_interface.dump_routing_table(f"{dump_path}/{ROUTE_MRT_FILE}")
            # Sleep for a while to wait for the dumping
            sleep(1.5)
        elif isinstance(router_interface, BIRDRouter):
            # For BIRD bgpd, dumping is periodic, we set the period as 1 second.
            router_interface.dump_routing_table(f"{dump_path}/{ROUTE_MRT_FILE}")
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
                                f"{dump_path}/{ROUTER_CONFIG_PKL_FILE}")
        save_variable_to_file(test_case, 
                                f"{dump_path}/{TESTCASE_PKL_FILE}")
        
        # Allow user to access the dumped directory
        allow_user_access(dump_path)

        ########## End the routing software instance and clients ##########
        
        self.tcp_client.end()
        router_interface.wait_for_log() # Shut down the clients one by one.
        self.exabgp_client.end()
        router_interface.end_bgp_instance()

        ###### Recover if the routing software crashes ######

        if router_interface.if_crashed():
            print("Software crashed! Recovering...")
            # (Currently) Save the router configuration and the testcase
            # to a special folder and restart.
            self.save_crash_setting(router_config=router_configuration,
                                    test_case=test_case,
                                    name=f"single_testcase_{get_current_time()}")
            self.tcp_client.end()
            self.exabgp_client.end()
            # Restart and wait for a while
            router_interface.recover_from_crash()
            sleep(1)

    def run_test_batch(self, 
                       test_batch_name: str,
                       router_configuration: RouterConfiguration):
        """
        Run the test in batch, and dump the result into the target directory.
        """

        ######### Initialize the router interface ##########

        router_interface = get_router_interface(router_configuration)

        ######### Prepare the directory for dumping #########
        
        data_file_path = f"{REPO_ROOT_PATH}/test_batches/{test_batch_name}.pkl"
        dump_dir_path = f"{REPO_ROOT_PATH}/{TESTCASE_DUMP_BATCHED}/{test_batch_name}"
        if directory_exists(dump_dir_path):
            os.system(f"sudo rm -r {dump_dir_path}")
        create_dir(dump_dir_path)
        dump_dir_path = f"{dump_dir_path}/data"
        create_dir(dump_dir_path)

        ########## Enumerate the testcases ##########

        # First read out the testcases
        testcase_list = read_variables_from_file(data_file_path)[0]
        
        for i in range(0,len(testcase_list)):

            print(f"======= Running testcase {i+1} =======")
            
            ###### Prepare for dumping ######

            testcase_dump_dir_path = f"{dump_dir_path}/testcase_{i+1}"
            create_dir(testcase_dump_dir_path)

            test_case = testcase_list[i]

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
                router_interface.dump_updates(f"{testcase_dump_dir_path}/{MESSAGE_MRT_FILE}")
            elif isinstance(router_interface, BIRDRouter):
                # For BIRD bgpd, we start to dump ALL BGP messages here.
                router_interface.dump_messages(f"{testcase_dump_dir_path}/{MESSAGE_MRT_FILE}")
            else:
                # This should not happen...
                raise ValueError("Unexpected type of the router interface!")

            try:
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
                        raise ValueError("Routing daemon crashed!")
                
                ###### Main part of dumping ######
            
                # Wait for the ExaBGP log to be ready
                sleep(2)

                # Get the contents for bgpd log and exabgp log
                bgpd_log_content = router_interface.read_log()
                exabgp_log_content = self.exabgp_client.read_log()
                # Clear the bgpd log
                # There is no need to clear the exabgp log since it will be overwritten 
                router_interface.clear_log()
                # Create bgpd log and exabgp log
                create_file(f"{testcase_dump_dir_path}/{BGPD_LOG_FILE}", bgpd_log_content)
                create_file(f"{testcase_dump_dir_path}/{EXABGP_LOG_FILE}", exabgp_log_content)
                # Dump the testcase settings
                save_variable_to_file(router_configuration, 
                                    f"{testcase_dump_dir_path}/{ROUTER_CONFIG_PKL_FILE}")
                save_variable_to_file(test_case,
                                    f"{testcase_dump_dir_path}/{TESTCASE_PKL_FILE}")

                # Dumping RIB here, different behaviors for different BGP softwares
                if isinstance(router_interface, FRRRouter):
                    # For FRRouting bgpd, dumping RIB is like taking a snapshot.
                    router_interface.dump_routing_table(f"{testcase_dump_dir_path}/{ROUTE_MRT_FILE}")
                    # Sleep for a while to wait for the dumping
                    sleep(1.5)
                elif isinstance(router_interface, BIRDRouter):
                    # For BIRD bgpd, dumping is periodic, we set the period as 1 second.
                    router_interface.dump_routing_table(f"{testcase_dump_dir_path}/{ROUTE_MRT_FILE}")
                    # So we need to sleep longer
                    sleep(2)

                # Stop MRT dumping, different behaviors for different BGP softwares
                if isinstance(router_interface, FRRRouter):
                    router_interface.stop_dump_updates()
                    router_interface.stop_dump_routing_table()
                elif isinstance(router_interface, BIRDRouter):
                    router_interface.stop_dump_messages()
                    router_interface.stop_dump_routing_table()
            
                ###### End the routing software instance and clients ######
                
                self.tcp_client.end()
                router_interface.wait_for_log() # Shut down the clients one by one.
                self.exabgp_client.end()
                router_interface.end_bgp_instance()

            except:
                pass

            ###### Deal with software crash ######

            if router_interface.if_crashed():
                print("Software crashed! Recovering...")
                # Save the router configuration and the testcase to a special folder.
                self.save_crash_setting(router_config=router_configuration,
                                        test_case=test_case,
                                        name=f"{test_batch_name}_testcase_{i+1}_{get_current_time()}")
                self.tcp_client.end()
                self.exabgp_client.end()
                # Mark the testcase has crashed
                create_file(f"{testcase_dump_dir_path}/{CRASH_MARKER_FILE}", "1")
                # Restart and wait for a while
                router_interface.recover_from_crash()
                sleep(1)
            
            ###### Clear the states and restart the software ######

            self.tcp_client.end()
            self.exabgp_client.end()
            router_interface.restart_software()

    def run_test_repeated(self,
                          testcase_name: str,
                          test_case: TestCase,
                          router_configuration: RouterConfiguration,
                          repeated_num: int):
        """
        Run the testcase repeatedly.
        """

        ######### Initialize the router interface ##########

        router_interface = get_router_interface(router_configuration)

        ######### Prepare the directory for dumping #########
        
        dump_dir_path = f"{REPO_ROOT_PATH}/{TESTCASE_DUMP_REPEATED}/{testcase_name}"
        if directory_exists(dump_dir_path):
            os.system(f"sudo rm -r {dump_dir_path}")
        create_dir(dump_dir_path)

        ########## Enumerate the testcases ##########
        
        for i in range(0,repeated_num):

            print(f"======= Running testcase {i+1} =======")
            
            ###### Prepare for dumping ######

            testcase_dump_dir_path = f"{dump_dir_path}/execution_{i+1}"
            create_dir(testcase_dump_dir_path)
            
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
                router_interface.dump_updates(f"{testcase_dump_dir_path}/{MESSAGE_MRT_FILE}")
            elif isinstance(router_interface, BIRDRouter):
                # For BIRD bgpd, we start to dump ALL BGP messages here.
                router_interface.dump_messages(f"{testcase_dump_dir_path}/{MESSAGE_MRT_FILE}")
            else:
                # This should not happen...
                raise ValueError("Unexpected type of the router interface!")

            try:
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
                        raise ValueError("Routing daemon crashed!")
                
                ###### Main part of dumping ######
            
                # Wait for the ExaBGP log to be ready
                sleep(2)

                # Get the contents for bgpd log and exabgp log
                bgpd_log_content = router_interface.read_log()
                exabgp_log_content = self.exabgp_client.read_log()
                # Clear the bgpd log
                # There is no need to clear the exabgp log since it will be overwritten 
                router_interface.clear_log()
                # Create bgpd log and exabgp log
                create_file(f"{testcase_dump_dir_path}/{BGPD_LOG_FILE}", bgpd_log_content)
                create_file(f"{testcase_dump_dir_path}/{EXABGP_LOG_FILE}", exabgp_log_content)
                # Dump the testcase settings
                save_variable_to_file(router_configuration, 
                                    f"{testcase_dump_dir_path}/{ROUTER_CONFIG_PKL_FILE}")
                save_variable_to_file(test_case,
                                    f"{testcase_dump_dir_path}/{TESTCASE_PKL_FILE}")
                
                # Dumping RIB here, different behaviors for different BGP softwares
                if isinstance(router_interface, FRRRouter):
                    # For FRRouting bgpd, dumping RIB is like taking a snapshot.
                    router_interface.dump_routing_table(f"{testcase_dump_dir_path}/{ROUTE_MRT_FILE}")
                    # Sleep for a while to wait for the dumping
                    sleep(1.5)
                elif isinstance(router_interface, BIRDRouter):
                    # For BIRD bgpd, dumping is periodic, we set the period as 1 second.
                    router_interface.dump_routing_table(f"{testcase_dump_dir_path}/{ROUTE_MRT_FILE}")
                    # So we need to sleep longer
                    sleep(2)
                
                # Stop MRT dumping, different behaviors for different BGP softwares
                if isinstance(router_interface, FRRRouter):
                    router_interface.stop_dump_updates()
                    router_interface.stop_dump_routing_table()
                elif isinstance(router_interface, BIRDRouter):
                    router_interface.stop_dump_messages()
                    router_interface.stop_dump_routing_table()
                
                ###### End the routing software instance and clients ######
                
                self.tcp_client.end()
                router_interface.wait_for_log() # Shut down the clients one by one.
                self.exabgp_client.end()
                router_interface.end_bgp_instance()
            
            except:
                pass

            ###### Deal with software crash ######

            if router_interface.if_crashed():
                print("Software crashed! Recovering...")
                # Save the router configuration and the testcase to a special folder.
                self.save_crash_setting(router_config=router_configuration,
                                        test_case=test_case,
                                        name=f"{testcase_name}_execution_{i+1}_{get_current_time()}")
                self.tcp_client.end()
                self.exabgp_client.end()
                # Mark the testcase has crashed
                create_file(f"{testcase_dump_dir_path}/{CRASH_MARKER_FILE}", "1")
                # Restart and wait for a while
                router_interface.recover_from_crash()
            
            ###### Clear the states and restart the software ######

            self.tcp_client.end()
            self.exabgp_client.end()
            router_interface.restart_software()

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
                              f"{dump_path}/{ROUTER_CONFIG_PKL_FILE}")
        save_variable_to_file(test_case,
                              f"{dump_path}/{TESTCASE_PKL_FILE}")
