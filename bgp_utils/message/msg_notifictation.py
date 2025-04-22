from ..binary_field_node import BinaryFieldNode
from ..basic_bfn_types import Number_BFN, ASN_BFN, Length_BFN, IPv4Address_BFN, BinaryFieldList_BFN
from .msg_base import MessageType, MessageType_BFN, HeaderMarker_BFN, MessageContent_BFN, BaseMessage_BFN
from data_utils.binary_utils import num2bytes
from enum import Enum
from functools import partial
import random
import numpy as np
