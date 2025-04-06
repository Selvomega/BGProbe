from network_utils import tcp_client, utils
import time

# BGP requires each peer to have a unique IP address.
# So you must setup a separate loopback interface. 

# ip = utils.gcloud_get_instance_ip("frr-instance")
ip = "127.0.0.1"

tcp_client = tcp_client.TCPClient(ip, 179)
tcp_client.start()
time.sleep(10)
tcp_client.end()
