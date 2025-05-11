from ..binary_field_node import BinaryFieldNode
from ..basic_bfn_types import Length_BFN, ASN_BFN, BinaryFieldList_BFN, Reserved_BFN, IPv4Address_BFN, IPv4Prefix_BFN
from .attr_base import AttrType_BFN, AttrLength_BFN, AttrValue_BFN, BaseAttr_BFN, PathAttributeType
from basic_utils.binary_utils import num2bytes, bytes2num
from enum import Enum
from functools import partial
import random
import numpy as np

class AFI(Enum):
    """
    Address Family Identifier (AFI)
    """
    RESERVED = 0
    IPV4 = 1
    IPV6 = 2
    NSAP = 3

class SAFI(Enum):
    """
    Subsequent Address Family Identifier (SAFI)
    """
    RESERVED = 0
    UNICAST = 1
    MULTICAST = 2

class AFI_BFN(BinaryFieldNode):
    """
    Address Family Identifier (AFI) BFN
    """
    def __init__(self, 
                 afi: AFI):
        """Initialize the AFI BFN."""

        ###### Basic attributes ######

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(AFI_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        self.afi : AFI = afi
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "AFI_BFN"

    ########## Get binary info ##########

    def get_binary_expression_inner(self):
        """Get binary expression."""
        return num2bytes(self.afi.value,2)
    
    ########## Update according to dependencies ##########
    
    def update_on_dependencies_inner(self):
        """
        Update the current BFN according to its dependencies.
        This BFN do not have dependencies.
        """
        # You should not raise error because of `attach` function
        return
    
    ########## Methods for generating random mutation ##########

    def random_afi(self):
        """
        Return a random AFI.
        The returned value is guaranteed to be a valid AFI.
        """
        valid_afis = [
            member for member in AFI if member != AFI.RESERVED
        ]
        return random.choice(valid_afis)
    
    ########## Methods for applying mutation ##########

    @BinaryFieldNode.set_function_decorator
    def set_afi(self,afi: AFI):
        """
        Set the AFI.
        """
        self.afi = afi
    
    @BinaryFieldNode.set_function_decorator
    def set_afi_val(self, afi_val: bytes):
        """
        Set the AFI value of current BFN.
        Will set the binary content directly.
        But this is still not equivalent to the `set_bval` function,
        because of the overwriting rules. 
        """
        self.binary_content = afi_val
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set + [
        BinaryFieldNode.MutationItem(random_afi, set_afi),
        BinaryFieldNode.MutationItem(
            partial(BinaryFieldNode.random_bval_fixed_len, 
                    length=2), 
            set_afi_val
        )
    ]

class SAFI_BFN(BinaryFieldNode):
    """
    Subsequent Address Family Identifier (SAFI)
    """
    def __init__(self, 
                 safi: SAFI):
        """Initialize the SAFI BFN."""

        ###### Basic attributes ######

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(SAFI_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        self.safi : SAFI = safi
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "SAFI_BFN"

    ########## Get binary info ##########

    def get_binary_expression_inner(self):
        """Get binary expression."""
        return num2bytes(self.safi.value,1)
    
    ########## Update according to dependencies ##########
    
    def update_on_dependencies_inner(self):
        """
        Update the current BFN according to its dependencies.
        This BFN do not have dependencies.
        """
        # You should not raise error because of `attach` function
        return
    
    ########## Methods for generating random mutation ##########

    def random_safi(self):
        """
        Return a random SAFI.
        The returned value is guaranteed to be a valid AFI.
        """
        valid_safis = [
            member for member in SAFI if member != SAFI.RESERVED
        ]
        return random.choice(valid_safis)
    
    ########## Methods for applying mutation ##########

    @BinaryFieldNode.set_function_decorator
    def set_safi(self,safi: SAFI):
        """
        Set the SAFI.
        """
        self.safi = safi
    
    @BinaryFieldNode.set_function_decorator
    def set_safi_val(self, safi_val: bytes):
        """
        Set the SAFI value of current BFN.
        Will set the binary content directly.
        But this is still not equivalent to the `set_bval` function,
        because of the overwriting rules. 
        """
        self.binary_content = safi_val
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set + [
        BinaryFieldNode.MutationItem(random_safi, set_safi),
        BinaryFieldNode.MutationItem(
            partial(BinaryFieldNode.random_bval_fixed_len, 
                    length=1), 
            set_safi_val
        )
    ]

class MPNLRI_BFN(BinaryFieldList_BFN):
    """
    BGP Network Layer Reachability Information (NLRI) for MultiProtocol BGP.
    """
    def __init__(self,
                 bfn_list : list):
        """Initialize by calling BinaryFieldList_BFN's `__init__` method."""
        super().__init__(bfn_list, "MPNLRIPrefix_BFN", BFN_type_check=False)

MPNextHop_BFN = BinaryFieldNode

class MPWithdrawnRoutes_BFN(BinaryFieldList_BFN):
    """
    BGP Withdrawn Routes field for MultiProtocol BGP.
    """
    def __init__(self,
                 bfn_list : list):
        """Initialize by calling BinaryFieldList_BFN's `__init__` method."""
        super().__init__(bfn_list, "MPWithdrawnRoute_BFN", BFN_type_check=False)

# +---------------------------------------------------------+
# |          Address Family Identifier (2 octets)           |
# +---------------------------------------------------------+
# |     Subsequent Address Family Identifier (1 octet)      |
# +---------------------------------------------------------+
# |      Length of Next Hop Network Address (1 octet)       |
# +---------------------------------------------------------+
# |         Network Address of Next Hop (variable)          |
# +---------------------------------------------------------+
# |                   Reserved (1 octet)                    |
# +---------------------------------------------------------+
# |    Network Layer Reachability Information (variable)    |
# +---------------------------------------------------------+

class MPReachNLRI_BFN(BinaryFieldNode):
    """
    Value of BGP MP_REACH_NLRI path attribute. 
    """
    def __init__(self,
                 afi_bfn: AFI_BFN,
                 safi_bfn: SAFI_BFN,
                 mp_nexthop_bfn: MPNextHop_BFN,
                 mp_nlri_bfn: MPNLRI_BFN,
                 mp_nexthop_len_bfn: Length_BFN = None,
                 reserved_bfn: Reserved_BFN = None):
        """Initialize the BGP MP_REACH_NLRI path attribute value."""

        ###### Redefine default input parameters to avoid shallow-copy ######

        if reserved_bfn is None:
            reserved_bfn = Reserved_BFN(reserved_val=b'\x00')
        if mp_nexthop_len_bfn is None:
            mp_nexthop_len_bfn = Length_BFN(length_val=0,length_byte_len=1)
        
        ###### Basic attributes ######

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(MPReachNLRI_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        # No special attributes

        ###### Deal with relations with and between children ######

        # Initialize the children. 
        # The sequence is very important.
        # Parents can still be `None`
        self.afi_key = self.append_child(afi_bfn)
        self.safi_key = self.append_child(safi_bfn)
        self.mp_nexthop_len_key = self.append_child(mp_nexthop_len_bfn)
        self.mp_nexthop_key = self.append_child(mp_nexthop_bfn)
        self.reserved_key = self.append_child(reserved_bfn)
        self.mp_nlri_key = self.append_child(mp_nlri_bfn)
        # Update the detach state of the current BFN.
        self.detach_according_to_children()
        # Add dependencies between children
        self.add_dependency_between_children(dependent_key=self.mp_nexthop_len_key,
                                             dependency_key=self.mp_nexthop_key)
        # Let children update
        self.children_update()
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "MPReachNLRI_BFN"

    ########## Get binary info ##########

    def get_binary_expression_inner(self):
        """Get binary expression."""
        # Concatenate the children's binary expressions.
        return b''.join([
            child.get_binary_expression() for child in self.children.values()
        ])
    
    ########## Update according to dependencies ##########
    
    def update_on_dependencies_inner(self):
        """
        Update the current BFN according to its dependencies.
        This BFN do not have dependencies.
        """
        # You should not raise error because of `attach` function
        return
    
    ########## Methods for generating random mutation ##########

    # Use methods from father class

    ########## Methods for applying mutation ##########

    # The following methods are recursively calling set-function of childrens, 
    # so there is no need to use `set_function_decorator`

    def set_afi(self, afi: AFI):
        """Set the AFI field."""
        bfn: AFI_BFN = self.children[self.afi_key]
        bfn.set_afi(afi)
    
    def set_afi_val(self, afi_val: bytes):
        """Set the binary value of the AFI field."""
        bfn: AFI_BFN = self.children[self.afi_key]
        bfn.set_afi_val(afi_val)
    
    def set_safi(self, safi: SAFI):
        """Set the SAFI field."""
        bfn: SAFI_BFN = self.children[self.safi_key]
        bfn.set_safi(safi)
    
    def set_safi_val(self, safi_val: bytes):
        """Set the binary value of the SAFI field."""
        bfn: SAFI_BFN = self.children[self.safi_key]
        bfn.set_safi_val(safi_val)

    def set_mp_nexthop_len(self, length: int):
        """Set the length of MP NextHop field."""
        bfn: Length_BFN = self.children[self.mp_nexthop_len_key]
        bfn.set_length(length)
    
    def set_mp_nexthop_bval(self, mp_nexthop_bval: bytes):
        """Set the binary value of MP NextHop field."""
        bfn: MPNextHop_BFN = self.children[self.mp_nexthop_key]
        bfn.set_bval(mp_nexthop_bval)
    
    def set_reserved_val(self, reserved_val: bytes):
        """Set the binary value of the Reserved field."""
        bfn: Reserved_BFN = self.children[self.reserved_key]
        bfn.set_reserved_val(reserved_val)
    
    def set_mp_nlri_bval(self, mp_nlri_bval: bytes):
        """Set the binary value of MP NLRI field."""
        bfn: MPNLRI_BFN = self.children[self.mp_nlri_key]
        bfn.set_bval(mp_nlri_bval)
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set

# +---------------------------------------------------------+
# |          Address Family Identifier (2 octets)           |
# +---------------------------------------------------------+
# |     Subsequent Address Family Identifier (1 octet)      |
# +---------------------------------------------------------+
# |               Withdrawn Routes (variable)               |
# +---------------------------------------------------------+

class MPUnreachNLRI_BFN(BinaryFieldNode):
    """
    Value of BGP MP_UNREACH_NLRI path attribute. 
    """
    def __init__(self,
                 afi_bfn: AFI_BFN,
                 safi_bfn: SAFI_BFN,
                 mp_wroutes_bfn: MPWithdrawnRoutes_BFN):
        """Initialize the BGP MP_UNREACH_NLRI path attribute value."""
        
        ###### Basic attributes ######

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(MPUnreachNLRI_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        # No special attributes

        ###### Deal with relations with and between children ######

        # Initialize the children. 
        # The sequence is very important.
        # Parents can still be `None`
        self.afi_key = self.append_child(afi_bfn)
        self.safi_key = self.append_child(safi_bfn)
        self.mp_wroutes_key = self.append_child(mp_wroutes_bfn)
        # Update the detach state of the current BFN.
        self.detach_according_to_children()
        # Let children update
        self.children_update()
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "MPUnreachNLRI_BFN"

    ########## Get binary info ##########

    def get_binary_expression_inner(self):
        """Get binary expression."""
        # Concatenate the children's binary expressions.
        return b''.join([
            child.get_binary_expression() for child in self.children.values()
        ])
    
    ########## Update according to dependencies ##########
    
    def update_on_dependencies_inner(self):
        """
        Update the current BFN according to its dependencies.
        This BFN do not have dependencies.
        """
        # You should not raise error because of `attach` function
        return
    
    ########## Methods for generating random mutation ##########

    # Use methods from father class

    ########## Methods for applying mutation ##########

    # The following methods are recursively calling set-function of childrens, 
    # so there is no need to use `set_function_decorator`

    def set_afi(self, afi: AFI):
        """Set the AFI field."""
        bfn: AFI_BFN = self.children[self.afi_key]
        bfn.set_afi(afi)
    
    def set_afi_val(self, afi_val: bytes):
        """Set the binary value of the AFI field."""
        bfn: AFI_BFN = self.children[self.afi_key]
        bfn.set_afi_val(afi_val)
    
    def set_safi(self, safi: SAFI):
        """Set the SAFI field."""
        bfn: SAFI_BFN = self.children[self.safi_key]
        bfn.set_safi(safi)
    
    def set_safi_val(self, safi_val: bytes):
        """Set the binary value of the SAFI field."""
        bfn: SAFI_BFN = self.children[self.safi_key]
        bfn.set_safi_val(safi_val)
    
    def set_mp_wroutes_bval(self, mp_wroutes_bval: bytes):
        """Set the binary value of MP WithdrawnRoutes field."""
        bfn: MPWithdrawnRoutes_BFN = self.children[self.mp_wroutes_key]
        bfn.set_bval(mp_wroutes_bval)
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set

class MPReachNLRIAttr_BFN(BaseAttr_BFN):
    """
    BGP path attribute MP_REACH_NLRI.
    """
    def __init__(self, 
                 attr_value_bfn: MPReachNLRI_BFN, 
                 attr_len_bfn: AttrLength_BFN = None):
        """Initialize the BGP MP_REACH_NLRI path attribute"""

        ###### Redefine default input parameters to avoid shallow-copy ######

        if attr_len_bfn is None:
            attr_len_bfn = AttrLength_BFN(length_val=0)

        ###### Basic attributes ######

        super().__init__(attr_type_bfn=AttrType_BFN(PathAttributeType.MP_REACH_NLRI),
                         attr_len_bfn=attr_len_bfn,
                         attr_value_bfn=attr_value_bfn)

        ###### Set the weights ######
        self.weights = np.ones(len(MPReachNLRIAttr_BFN.mutation_set))
        self.weights /= np.sum(self.weights)
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "MPReachNLRIAttr_BFN"

    ########## Factory methods: Create an instance of the class ##########

    @classmethod
    def get_ipv4_unicast_bfn(cls,
                             mp_nexthop: str,
                             mp_nlri: list[str]) -> "MPReachNLRIAttr_BFN":
        """
        Get the MPReachNLRIAttr_BFN path attribute BFN for IPv4 UNICAST.
        """
        afi_bfn : AFI_BFN = AFI_BFN(afi=AFI.IPV4)
        safi_bfn : SAFI_BFN = SAFI_BFN(safi=SAFI.UNICAST)
        mp_nexthop_bfn = IPv4Address_BFN(mp_nexthop)
        mp_nlri_list = [IPv4Prefix_BFN.get_bfn(nlri_elem) for nlri_elem in mp_nlri]
        mp_nlri_bfn = MPNLRI_BFN(mp_nlri_list)
        mp_reach_nlri_bfn = MPReachNLRI_BFN(
            afi_bfn=afi_bfn,
            safi_bfn=safi_bfn,
            mp_nexthop_bfn=mp_nexthop_bfn,
            mp_nlri_bfn=mp_nlri_bfn
        )
        return MPReachNLRIAttr_BFN(
            attr_value_bfn=mp_reach_nlri_bfn
        )

    ########## Get binary info ##########

    # Use methods from father class
    
    ########## Update according to dependencies ##########
    
    # Use methods from father class

    ########## Methods for generating random mutation ##########

    # Use methods from father class

    ########## Methods for applying mutation ##########

    # The following methods are recursively calling set-function of childrens, 
    # so there is no need to use `set_function_decorator`

    def set_afi(self, afi: AFI):
        """Set the AFI field."""
        bfn: MPReachNLRI_BFN = self.children[self.attr_value_key]
        bfn.set_afi(afi)
    
    def set_afi_val(self, afi_val: bytes):
        """Set the binary value of the AFI field."""
        bfn: MPReachNLRI_BFN = self.children[self.attr_value_key]
        bfn.set_afi_val(afi_val)
    
    def set_safi(self, safi: SAFI):
        """Set the SAFI field."""
        bfn: MPReachNLRI_BFN = self.children[self.attr_value_key]
        bfn.set_safi(safi)
    
    def set_safi_val(self, safi_val: bytes):
        """Set the binary value of the SAFI field."""
        bfn: MPReachNLRI_BFN = self.children[self.attr_value_key]
        bfn.set_safi_val(safi_val)

    def set_mp_nexthop_len(self, length: int):
        """Set the length of MP NextHop field."""
        bfn: MPReachNLRI_BFN = self.children[self.attr_value_key]
        bfn.set_length(length)
    
    def set_mp_nexthop_bval(self, mp_nexthop_bval: bytes):
        """Set the binary value of MP NextHop field."""
        bfn: MPReachNLRI_BFN = self.children[self.attr_value_key]
        bfn.set_bval(mp_nexthop_bval)
    
    def set_reserved_val(self, reserved_val: bytes):
        """Set the binary value of the Reserved field."""
        bfn: MPReachNLRI_BFN = self.children[self.attr_value_key]
        bfn.set_reserved_val(reserved_val)
    
    def set_mp_nlri_bval(self, mp_nlri_bval: bytes):
        """Set the binary value of MP NLRI field."""
        bfn: MPReachNLRI_BFN = self.children[self.attr_value_key]
        bfn.set_bval(mp_nlri_bval)

    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BaseAttr_BFN.mutation_set

class MPUnreachNLRIAttr_BFN(BaseAttr_BFN):
    """
    BGP path attribute MP_UNREACH_NLRI.
    """
    def __init__(self, 
                 attr_value_bfn: MPUnreachNLRI_BFN, 
                 attr_len_bfn: AttrLength_BFN = None):
        """Initialize the BGP MP_UNREACH_NLRI path attribute"""

        ###### Redefine default input parameters to avoid shallow-copy ######

        if attr_len_bfn is None:
            attr_len_bfn = AttrLength_BFN(length_val=0)

        ###### Basic attributes ######

        super().__init__(attr_type_bfn=AttrType_BFN(PathAttributeType.MP_UNREACH_NLRI),
                         attr_len_bfn=attr_len_bfn,
                         attr_value_bfn=attr_value_bfn)

        ###### Set the weights ######
        self.weights = np.ones(len(MPUnreachNLRIAttr_BFN.mutation_set))
        self.weights /= np.sum(self.weights)
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "MPUnreachNLRIAttr_BFN"

    ########## Factory methods: Create an instance of the class ##########

    @classmethod
    def get_ipv4_unicast_bfn(cls,
                             mp_wroutes: list[str]) -> "MPUnreachNLRIAttr_BFN":
        """
        Get the MP_UNREACH_NLRI path attribute BFN for IPv4 UNICAST.
        """
        afi_bfn : AFI_BFN = AFI_BFN(afi=AFI.IPV4)
        safi_bfn : SAFI_BFN = SAFI_BFN(safi=SAFI.UNICAST)
        mp_wroutes_list = [IPv4Prefix_BFN.get_bfn(wroute) for wroute in mp_wroutes]
        mp_wroutes_bfn = MPWithdrawnRoutes_BFN(mp_wroutes_list)
        mp_unreach_nlri_bfn = MPUnreachNLRI_BFN(
            afi_bfn=afi_bfn,
            safi_bfn=safi_bfn,
            mp_wroutes_bfn=mp_wroutes_bfn
        )
        return MPUnreachNLRIAttr_BFN(
            attr_value_bfn=mp_unreach_nlri_bfn
        )

    ########## Get binary info ##########

    # Use methods from father class
    
    ########## Update according to dependencies ##########
    
    # Use methods from father class

    ########## Methods for generating random mutation ##########

    # Use methods from father class

    ########## Methods for applying mutation ##########

    # The following methods are recursively calling set-function of childrens, 
    # so there is no need to use `set_function_decorator`

    def set_afi(self, afi: AFI):
        """Set the AFI field."""
        bfn: MPUnreachNLRI_BFN = self.children[self.attr_value_key]
        bfn.set_afi(afi)
    
    def set_afi_val(self, afi_val: bytes):
        """Set the binary value of the AFI field."""
        bfn: MPUnreachNLRI_BFN = self.children[self.attr_value_key]
        bfn.set_afi_val(afi_val)
    
    def set_safi(self, safi: SAFI):
        """Set the SAFI field."""
        bfn: MPUnreachNLRI_BFN = self.children[self.attr_value_key]
        bfn.set_safi(safi)
    
    def set_safi_val(self, safi_val: bytes):
        """Set the binary value of the SAFI field."""
        bfn: MPUnreachNLRI_BFN = self.children[self.attr_value_key]
        bfn.set_safi_val(safi_val)
    
    def set_mp_wroutes_bval(self, mp_wroutes_bval: bytes):
        """Set the binary value of MP WithdrawnRoutes field."""
        bfn: MPUnreachNLRI_BFN = self.children[self.attr_value_key]
        bfn.set_bval(mp_wroutes_bval)

    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BaseAttr_BFN.mutation_set
