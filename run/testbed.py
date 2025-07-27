# This file ddefines the testbed for BGProbe

# Difference between a "test" and a "testcase"
# - A test is the whole process, including testcase running, log dumping and crash recovering, and may contain multiple such runs.
# - A testcase is just the content executed in a single run.

# Difference between `test_name` and `testcase_id`:
# - `test_name` is the name of the test. It is just used to indicate a test, and can be reused. 
# - `testcase_id` is a UNIQUE identification of a single testcase (Please recall the difference between "test" and "testcase"). 

from time import sleep
from basic_utils.serialize_utils import save_variable_to_file, read_variables_from_file
from basic_utils.time_utils import get_current_time
from basic_utils.file_utils import *
from basic_utils.const import *
from testcase_factory.basic_types import Halt, TestCase
from test_agents.tcp_agent import TCPAgent, TCPAgentConfiguration
from test_agents.router_agent import RouterAgentConfiguration, FRRRouterAgent, BIRDRouterAgent, GoBGPRouterAgent, OpenBGPDRouterAgent, get_router_agent
from test_agents.exabgp_agent import ExaBGPAgent, ExaBGPAgentConfiguration
from testcase_factory.single_testcase_factory import single_testcase_suite
from subprocess import CalledProcessError

MESSAGE_MRT_FILE = "messages.mrt"
ROUTE_MRT_FILE = "routes.mrt"
EXABGP_LOG_FILE = "exabgp.log"
BGPD_LOG_FILE = "bgpd.log"
ROUTER_CONFIG_PKL_FILE = "router_conf.pkl"
ROUTER_CONFIG_TXT_FILE = "router_conf.txt"
TESTCASE_PKL_FILE = "testcase.pkl"
TESTCASE_TXT_FILE = "testcase.txt"
CRASH_MARKER_FILE = "crashed"

TEMP_DUMP_DIR = f"{REPO_ROOT_PATH}/data/temp_dump"
TEMP_MESSAGE_DUMP = f"{TEMP_DUMP_DIR}/{MESSAGE_MRT_FILE}"
TEMP_ROUTE_DUMP = f"{TEMP_DUMP_DIR}/{ROUTE_MRT_FILE}"
TEMP_EXABGP_DUMP = f"{TEMP_DUMP_DIR}/{EXABGP_LOG_FILE}"
TEMP_BGPD_DUMP = f"{TEMP_DUMP_DIR}/{BGPD_LOG_FILE}"

class Testbed:
    """
    BGProbe testbed. 
    """
    def __init__(self,
                 tcp_agent_config: TCPAgentConfiguration,
                 router_agent_config: RouterAgentConfiguration,
                 exabgp_agent_config: ExaBGPAgentConfiguration
                 ):
        """
        Initialize the test agent for the BGP software
        """
        # First-stage initialization
        self.tcp_agent_config : TCPAgentConfiguration = tcp_agent_config
        self.router_agent_config: RouterAgentConfiguration = router_agent_config
        self.exabgp_agent_config : ExaBGPAgentConfiguration = exabgp_agent_config
        # Initialize the agents
        self.tcp_agent = TCPAgent(self.tcp_agent_config)
        self.router_agent = get_router_agent(self.router_agent_config)
        self.exabgp_agent = ExaBGPAgent(self.exabgp_agent_config)

    def single_test_inner(self,
                          testcase: TestCase,
                          dump_path: str,
                          testcase_id: str):
        """
        The inner function of running a single testcase.
        Includes testcase running, file dumping and crash recovery.

        `dump_path`: The path of the dumping directory, must be prepared.

        After the current test, the following items will be saved to `dump_path`:
        - CRASH_MARKER_FILE: Depending on whether the testcase causes a software crash
        - MESSAGE_MRT_FILE: Messages the software received
        - ROUTE_MRT_FILE: RIB of the target BGP instance
        - BGPD_LOG_FILE, EXABGP_LOG_FILE: The log of the two BGP instances
        - ROUTER_CONFIG_PKL_FILE, TESTCASE_PKL_FILE: Saved configuration of the testcase

        `testcase_id`: The unique ID used to indicate the testcase.

        `testcase_id` may be used in the following instances:
        - Saving the crash setting 

        """

        ########## Allow user to access the dumped directory ##########

        allow_user_access(dump_path)

        ########## Initialize the routing software interface. ##########

        self.router_agent.clear_log() 

        ########## Define the crash handling function. ##########

        def crash_handling():
            """
            Handle software crashes.
            """
            # Allow user to access the dumped directory
            allow_user_access(dump_path)
            # Create a marker file in `dump_path`.
            if self.router_agent.if_crashed():
                print("Software crashed!")
                # Save the router configuration and the testcase to a special folder.
                self.save_crash_setting(router_agent_config=self.router_agent_config,
                                        testcase=testcase,
                                        name=testcase_id)
                # Mark the testcase has crashed
                create_file(f"{dump_path}/{CRASH_MARKER_FILE}", "1")
            # Clear the test pipeline 
            self.tcp_agent.end()
            self.exabgp_agent.end()
            self.router_agent.end_bgp_instance()
            self.router_agent.restart_software()

        ########## Start the routing software instance and clients ##########

        if isinstance(self.router_agent, GoBGPRouterAgent):
            self.router_agent.message_mrt_dump_config(f"{dump_path}/{MESSAGE_MRT_FILE}")
            self.router_agent.route_mrt_dump_config(f"{dump_path}/{ROUTE_MRT_FILE}")
        elif isinstance(self.router_agent, OpenBGPDRouterAgent):
            self.router_agent.message_mrt_dump_config(f"{dump_path}/{MESSAGE_MRT_FILE}")
            self.router_agent.route_mrt_dump_config(f"{dump_path}/{ROUTE_MRT_FILE}")
        self.router_agent.start_bgp_instance()
        self.router_agent.wait_for_log() # Start the clients one by one.
        self.exabgp_agent.start()
        self.router_agent.wait_for_log() # Start the clients one by one.
        self.tcp_agent.start()

        ########## Dumping BGP messages ##########

        # Different dumping behavior for different BGP softwares
        if isinstance(self.router_agent, FRRRouterAgent):
            # For FRRouting bgpd, we start to dump ONLY BGP UPDATE messages here.
            self.router_agent.dump_updates(f"{dump_path}/{MESSAGE_MRT_FILE}")
        elif isinstance(self.router_agent, BIRDRouterAgent):
            # For BIRD bgpd, we start to dump ALL BGP messages here.
            self.router_agent.dump_messages(f"{dump_path}/{MESSAGE_MRT_FILE}")
        elif isinstance(self.router_agent, GoBGPRouterAgent):
            # The MRT file dumping of GoBGPRouterAgent is set in the config file.
            pass
        elif isinstance(self.router_agent, OpenBGPDRouterAgent):
            # The MRT file dumping of OpenBGPDRouterAgent is set in the config file.
            pass
        else:
            # This should not happen...
            raise ValueError("Unexpected type of the router interface!")
        
        ########## Send test messages ##########

        # Send the message one-by-one
        for message in testcase:
            if isinstance(message, Halt):
                print("Halting between BGP messages to ensure fully updating...")
                sleep(2)
                continue
            self.tcp_agent.send(message.get_binary_expression())
            self.router_agent.wait_for_log() # Wait the state to become stable.
            if self.router_agent.if_crashed():
                crash_handling()
                return
        
        ########## Dumping BGP logs ##########
        
        # Wait for the ExaBGP log to be ready
        sleep(2)

        # Get the contents for bgpd log and exabgp log
        bgpd_log_content = self.router_agent.read_log()
        exabgp_log_content = self.exabgp_agent.read_log()
        # There is no need to clear the exabgp log since it will be overwritten 
        self.router_agent.clear_log()
        # Create bgpd log and exabgp log
        create_file(f"{dump_path}/{BGPD_LOG_FILE}", bgpd_log_content)
        create_file(f"{dump_path}/{EXABGP_LOG_FILE}", exabgp_log_content)

        ########## Dump the testcase settings ##########

        save_variable_to_file(self.router_agent_config, 
                              f"{dump_path}/{ROUTER_CONFIG_PKL_FILE}")
        save_variable_to_file(testcase, 
                              f"{dump_path}/{TESTCASE_PKL_FILE}")
        create_file(f"{dump_path}/{ROUTER_CONFIG_TXT_FILE}",
                    self.router_agent_config.get_string_expression())
        create_file(f"{dump_path}/{TESTCASE_TXT_FILE}",
                    testcase.get_string_expression())

        try:

            ########## Dumping RIB ##########

            # Dumping RIB here, different behaviors for different BGP softwares
            if isinstance(self.router_agent, FRRRouterAgent):
                # For FRRouting bgpd, dumping RIB is like taking a snapshot.
                self.router_agent.dump_routing_table(f"{dump_path}/{ROUTE_MRT_FILE}")
                # No need to sleep here since it is done in `dump_routing_table`
            elif isinstance(self.router_agent, BIRDRouterAgent):
                # For BIRD bgpd, dumping is periodic, we set the period as 1 second.
                self.router_agent.dump_routing_table(f"{dump_path}/{ROUTE_MRT_FILE}")
                # So we need to sleep longer
                sleep(2)
            elif isinstance(self.router_agent, GoBGPRouterAgent):
                # The MRT file dumping of GoBGPRouterAgent has been set in the config file.
                sleep(1)
            elif isinstance(self.router_agent, OpenBGPDRouterAgent):
                # The MRT file dumping of OpenBGPDRouterAgent as been set in the config file.
                sleep(1)
            else:
                # This should not happen...
                raise ValueError("Unexpected type of the router interface!")

            ########## Stop MRT dumping ##########

            if isinstance(self.router_agent, FRRRouterAgent):
                self.router_agent.stop_dump_updates()
                self.router_agent.stop_dump_routing_table()
            elif isinstance(self.router_agent, BIRDRouterAgent):
                self.router_agent.stop_dump_messages()
                self.router_agent.stop_dump_routing_table()
            elif isinstance(self.router_agent, GoBGPRouterAgent):
                pass
            elif isinstance(self.router_agent, OpenBGPDRouterAgent):
                pass
            else:
                # This should not happen...
                raise ValueError("Unexpected type of the router interface!")
            
        except CalledProcessError: 
            pass

        ########## Deal with software crashes ##########

        if self.router_agent.if_crashed():
            crash_handling()
            return
        
        ########## Clear the test pipeline ##########
                
        self.tcp_agent.end()
        self.router_agent.wait_for_log() # Shut down the clients one by one.
        self.exabgp_agent.end()
        self.router_agent.end_bgp_instance()
        self.router_agent.restart_software()


    # TODO: Deal with the dumping here: Can we make it a callback function?
    def run_test_single(self,
                        testcase: TestCase,
                        test_name: str):
        """
        Run a single testcase.

        `test_name`: The name of the test.
        """

        ########## Prepare the directory for dumping ##########

        # Since this is about a single test, `testcase_id` can be derived directly from the `test_name`.
        testcase_id = f"{test_name}_{get_current_time()}"
        dump_path = f"{REPO_ROOT_PATH}/{TESTCASE_DUMP_SINGLE}/{testcase_id}"
        assert not directory_exists(dump_path)
        create_dir(dump_path)

        ########## Run the test ##########

        self.single_test_inner(
            testcase=testcase,
            dump_path=dump_path,
            testcase_id=testcase_id,
        )
    
    def run_test_single_all(self,
                            test_name: str):
        """
        Run all single testcases.

        `test_name`: The name of the test.
        """

        ########## Prepare the directory for dumping ##########

        test_name_with_time = f"{test_name}_{get_current_time()}"

        dump_dir_path = f"{REPO_ROOT_PATH}/{TESTCASE_DUMP_SINGLE}/{test_name_with_time}"
        assert not directory_exists(dump_dir_path)
        create_dir(dump_dir_path)

        allow_user_access(dump_dir_path)

        ########## Enumerate the testcases ##########

        # First retrieve the testcases.
        testcase_list = single_testcase_suite
        for i in range(2,len(testcase_list)):

            print(f"======= Running testcase {i} =======")

            testcase_dump_dir_path = f"{dump_dir_path}/testcase_{i}"
            create_dir(testcase_dump_dir_path)
            testcase = testcase_list[i]

            self.single_test_inner(
                testcase=testcase,
                dump_path=testcase_dump_dir_path,
                # `testcase_id` is defined here
                testcase_id=f"{test_name_with_time}_testcase-{i}"
            )

    def run_test_batch(self, 
                       test_batch_name: str,
                       test_name: str):
        
        """
        Run the test in batch, and dump the result into the target directory.

        `test_batch_name`: The name of the file containing the generated testcases.
        `test_name`: The name of the test.
        """

        ######### Prepare the directory for dumping #########

        test_name_with_time = f"{test_name}_{get_current_time()}"
        
        data_file_path = f"{REPO_ROOT_PATH}/testcase_factory/batched_testcases/{test_batch_name}.pkl"
        dump_dir_path = f"{REPO_ROOT_PATH}/{TESTCASE_DUMP_BATCHED}/{test_name_with_time}"
        assert not directory_exists(dump_dir_path)
        create_dir(dump_dir_path)

        allow_user_access(dump_dir_path)

        ########## Enumerate the testcases ##########

        # First retrieve the testcases.
        testcase_list = read_variables_from_file(data_file_path)[0]
        
        for i in range(0,len(testcase_list)):

            print(f"======= Running testcase {i+1} =======")

            testcase_dump_dir_path = f"{dump_dir_path}/testcase_{i+1}"
            create_dir(testcase_dump_dir_path)
            testcase = testcase_list[i]

            self.single_test_inner(
                testcase=testcase,
                dump_path=testcase_dump_dir_path,
                # `testcase_id` is defined here
                testcase_id=f"{test_name_with_time}_testcase-{i+1}"
            )

    def run_test_repeated(self,
                          test_name: str,
                          testcase: TestCase,
                          repeated_num: int):
        """
        Run the testcase repeatedly.

        `test_name`: The name of the test.
        """

        ######### Prepare the directory for dumping #########

        test_name_with_time = f"{test_name}_{get_current_time()}"
        dump_path = f"{REPO_ROOT_PATH}/{TESTCASE_DUMP_REPEATED}/{test_name_with_time}"
        assert not directory_exists(dump_path)
        create_dir(dump_path)

        allow_user_access(dump_path)

        ########## Enumerate the testcases ##########
        
        for i in range(0,repeated_num):

            print(f"======= Running testcase {i+1} =======")

            testcase_dump_path = f"{dump_path}/execution_{i+1}"
            create_dir(testcase_dump_path)

            self.single_test_inner(
                testcase=testcase,
                dump_path=testcase_dump_path,
                # `testcase_id` is defined here
                testcase_id=f"{test_name_with_time}_execution-{i+1}"
            )
    
    def run_test_playground(self,
                            testcase: TestCase,
                            test_name: str):
        """
        Run a testcase in the playground.

        `test_name`: The name of the test.
        """

        ########## Prepare the directory for dumping ##########

        # Since this is about a single test, `testcase_id` can be derived directly from the `test_name`.
        testcase_id = f"{test_name}_{get_current_time()}"
        dump_path = f"{REPO_ROOT_PATH}/{TESTCASE_DUMP_PLAYGROUND}/{testcase_id}"
        assert not directory_exists(dump_path)
        create_dir(dump_path)

        allow_user_access(dump_path)

        ########## Run the test ##########

        self.single_test_inner(
            testcase=testcase,
            dump_path=dump_path,
            testcase_id=testcase_id,
        )

    def save_crash_setting(self,
                           router_agent_config: RouterAgentConfiguration,
                           testcase: TestCase,
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
        save_variable_to_file(router_agent_config,
                              f"{dump_path}/{ROUTER_CONFIG_PKL_FILE}")
        save_variable_to_file(testcase,
                              f"{dump_path}/{TESTCASE_PKL_FILE}")
        create_file(f"{dump_path}/{ROUTER_CONFIG_TXT_FILE}",
                    router_agent_config.get_string_expression())
        create_file(f"{dump_path}/{TESTCASE_TXT_FILE}",
                    testcase.get_string_expression())
