# This file is used to test the BGP router software with single testcase
# to observe in detail the bahavior of the router software

import sys, os, argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_agents.router_agent import *

from bgprobe_config import *

from testbed import *

testcase_id = 2
test_name = f"playground_random_attribute_bfn_{testcase_id}"
data_file_path = f"{REPO_ROOT_PATH}/testcase_factory/batched_testcases/random_attribute_bfn.pkl"
testcase = read_variables_from_file(data_file_path)[0][testcase_id-1]

########## Configure the Router Software ##########

router_agent_config = RouterAgentConfiguration(
    asn=router_agent_asn,
    router_id=router_agent_ip,
    neighbors=[
        Neighbor(
            peer_ip=tester_agent_ip,
            peer_asn=tester_agent_asn,
            local_source=router_agent["veth"]
        ),
        Neighbor(
            peer_ip=exabgp_agent_ip,
            peer_asn=exabgp_agent_asn,
            local_source=router_agent["veth"]
        ),
    ],
    router_type=router_type
)

########## Initialize the Testbed ##########

testbed = Testbed(
    tcp_agent_config = tcp_agent_config,
    router_agent_config = router_agent_config,
    exabgp_agent_config = exabgp_agent_config,
)

# testbed.run_test_playground(
#     testcase=testcase,
#     test_name=test_name,
# )

if __name__ == "__main__":
    # Create the arg parser. 
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--action", "-a",
        required=True,
        choices=["start_instance", 
                 "stop_instance", 
                 "send_msg", 
                 "start_dump_msg",
                 "stop_dump_msg",
                 "start_dump_rib", 
                 "stop_dump_rib", 
                 "print_log",
                 "clear_log"]
    )
    args = parser.parse_args()

    match args.action:
        case "start_instance":
            testbed.router_agent.start_bgp_instance()
            testbed.router_agent.clear_log()
        case "stop_instance": 
            testbed.router_agent.end_bgp_instance()
        case "send_msg":
            testbed.router_agent.wait_for_log() # Start the clients one by one.
            testbed.exabgp_agent.start()
            testbed.router_agent.wait_for_log() # Start the clients one by one.
            testbed.tcp_agent.start()
            print("Debug info: Ready!")
            
            # Send the message one-by-one
            for message in testcase:
                print("Debug info: Message sent!")
                if isinstance(message, Halt):
                    print("Halting between BGP messages to ensure fully updating...")
                    sleep(2)
                    continue
                testbed.tcp_agent.send(message.get_binary_expression())
                sleep(1)
                testbed.router_agent.wait_for_log() # Wait the state to become stable.
        case "start_dump_msg":
            mrt_path = f"{REPO_ROOT_PATH}/{TESTCASE_DUMP_PLAYGROUND}/{MESSAGE_MRT_FILE}"
            if isinstance(testbed.router_agent, FRRRouterAgent):
                # For FRRouting bgpd, we start to dump ONLY BGP UPDATE messages here.
                testbed.router_agent.dump_updates(mrt_path)
            elif isinstance(testbed.router_agent, BIRDRouterAgent):
                # For BIRD bgpd, we start to dump ALL BGP messages here.
                testbed.router_agent.dump_messages(mrt_path)
            else:
                # This should not happen...
                raise ValueError("Unexpected type of the router interface!")
        case "stop_dump_msg":
            if isinstance(testbed.router_agent, FRRRouterAgent):
                testbed.router_agent.stop_dump_updates()
            elif isinstance(testbed.router_agent, BIRDRouterAgent):
                testbed.router_agent.stop_dump_messages()
            else:
                # This should not happen...
                raise ValueError("Unexpected type of the router interface!")
        case "start_dump_rib":
            mrt_path = f"{REPO_ROOT_PATH}/{TESTCASE_DUMP_PLAYGROUND}/{ROUTE_MRT_FILE}"
            delete_file(mrt_path)
            if isinstance(testbed.router_agent, FRRRouterAgent):
                # For FRRouting bgpd, dumping RIB is like taking a snapshot.
                testbed.router_agent.dump_routing_table(mrt_path)
                # Sleep for a while to wait for the dumping
                sleep(1.5)
            elif isinstance(testbed.router_agent, BIRDRouterAgent):
                # For BIRD bgpd, dumping is periodic, we set the period as 1 second.
                testbed.router_agent.dump_routing_table(mrt_path)
                # So we need to sleep longer
                sleep(2)
            else:
                # This should not happen...
                raise ValueError("Unexpected type of the router interface!")
        case "stop_dump_rib":
            if isinstance(testbed.router_agent, FRRRouterAgent):
                testbed.router_agent.stop_dump_routing_table()
            elif isinstance(testbed.router_agent, BIRDRouterAgent):
                testbed.router_agent.stop_dump_routing_table()
            else:
                # This should not happen...
                raise ValueError("Unexpected type of the router interface!")
        case "print_log":
            bgpd_log_content = testbed.router_agent.read_log()
            print(bgpd_log_content)
        case "clear_log":
            testbed.router_agent.clear_log()
