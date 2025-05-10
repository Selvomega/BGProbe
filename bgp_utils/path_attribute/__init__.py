from .attr_base import PathAttributeType, calculate_attr_type_property, AttrType_BFN, AttrLength_BFN, AttrValue_BFN, BaseAttr_BFN
from .attr_origin import OriginType, Origin_BFN, OriginAttr_BFN
from .attr_aspath import PathSegementType, PathSegmentType_BFN, PathSegmentLength_BFN, ASNList_BFN, PathSegmentValue_BFN, PathSegment_BFN, ASPath_BFN, ASPathAttr_BFN
from .attr_nexthop import NextHop_BFN, NextHopAttr_BFN
from .attr_med import MED_BFN, MEDAttr_BFN
from .attr_locpref import LOCPREF_BFN, LOCPREFAttr_BFN
from .attr_communities import compose_communities_value, decompose_communities_value, WellKnownCommunities, SingleCommunity_BFN, Communities_BFN, CommunitiesAttr_BFN

from .attr_mpnlri import AFI, SAFI, AFI_BFN, SAFI_BFN, MPNLRI_BFN, MPNextHop_BFN, MPWithdrawnRoutes_BFN, MPReachNLRI_BFN, MPUnreachNLRI_BFN, MPReachNLRIAttr_BFN, MPUnreachNLRIAttr_BFN

from .attr_arbitrary import Arbitrary_BFN, ArbitraryAttr_BFN
