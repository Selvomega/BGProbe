"""
This file defines the TCP agent of BGProbe.
"""

from network_utils.tcp_client import TCPClientConfiguration, TCPClient

class TCPAgentConfiguration (TCPClientConfiguration):
    """
    Simply override the TCPClientConfiguration in `network_utils`.
    """
    pass

class TCPAgent(TCPClient):
    """
    Simply override the TCPClient in `network_utils`.
    """
    pass
