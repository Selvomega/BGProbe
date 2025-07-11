"""
This module defines the info types used by data analyzers
"""

from dataclasses import dataclass
from typing import TypedDict

@dataclass
class RouteInfo:
    """
    The info of routing table entries.
    """
    as_path: list[int]
    next_hop: str
    announced: str

@dataclass
class UpdateMessageInfo:
    """
    The info of received update messages.
    """
    from_as: int
    to_as: int
    as_path: list[int]
    next_hop: str
    announced: list[str]
    withdrawn: list[str]

@dataclass
class RouterLogInfo:
    """
    The info of router logs.
    """
    invalid: bool
    session_break: bool
    withdrawn: list[str]

@dataclass
class ExaBGPLogInfo:
    """
    The info of ExaBGP logs.
    """
    invalid: bool
    update_messages: list[UpdateMessageInfo]

class TestcaseReport(TypedDict):
    """
    The report of the outcome of a testcase.
    """
    testcase_id: str
    mrt_route_data: list[dict]
    mrt_update_message_data: list[dict]
    router_log_data: dict
    exabgp_log_data: dict
