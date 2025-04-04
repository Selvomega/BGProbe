from network_utils import tcp_client, utils

ip = utils.gcloud_get_instance_ip("frr-instance")

tcp_client = tcp_client.TCPClient(ip, 179)
tcp_client.start()
tcp_client.end()
