from .open_opt import ReadyToUseOptValue
from dataclasses import dataclass
from bgp_utils.basic_types import IP

# TODO: should we use type `IP` for the `ip_addr`?
@dataclass
class BGPClientConfiguration:
    """
    This class is used to configure the BGP client.
    """
    asn : int
    ip_addr : IP

# TODO: how should we deal with the configuration stuff?
def apply_configuration():
    """
    Apply the configuration to the current module.
    """
    pass
