import mrtparse
from .mrt_analyzer_base import BaseMRTAnalyzer
from ..utils import *
from ..basic_types import RouteInfo, UpdateMessageInfo
from basic_utils.file_utils import file_exists

class MRTParseMRTAnalyzer(BaseMRTAnalyzer):
    """
    MRT analyzer supported by mrtparse
    """

    @classmethod
    def read_mrt(cls, path: str):
        """
        Read the MRT file and return the results.
        """
        if not file_exists(path):
            return []
        reader = mrtparse.Reader(open(path, "rb"))
        ret_list = []
        for entry in reader:
            ret_list.append(entry.data)
        return ret_list

    @classmethod
    def get_route_data(cls, path):
        """
        Return a list of dict, each represents an entry in the routing table.
        Used to analyze RIB MRT files.
        Have to deal with the repeated items in the MRT file.
        
        `path`: indicates the path to the MRT file.
        """
        dict_mask_set = DictMaskSet([
            DictMask(["timestamp"]),
            DictMask(["type"]),
            DictMask(["subtype"]),
            DictMask(["length"]),
            DictMask(["sequence_number"]),
            DictMask(["rib_entries","peer_index"]),
            DictMask(["rib_entries","originated_time"]),
            DictMask(["rib_entries","path_attributes_length"]),
        ])
        mrt_dict_list = cls.read_mrt(path)
        ret_list = []
        for mrt_dict in mrt_dict_list:
            if retrieve_key(mrt_dict["subtype"]) in {2}:
                # The type is RIB_IPV4_UNICAST
                processed_dict = mask_dict(mrt_dict, dict_mask_set)
                if processed_dict not in ret_list: ret_list.append(processed_dict)
        return ret_list

    @classmethod
    def get_update_message_data(cls, path):
        """
        Return a list of dict, each represents an Update message received.
        Used to analyze message MRT files.
        
        `path`: indicates the path to the MRT file.
        """
        dict_mask_set = DictMaskSet([
            DictMask(["timestamp"]),
            DictMask(["type"]),
            DictMask(["subtype"]),
            DictMask(["length"]),
            DictMask(["ifindex"]),
            DictMask(["bgp_message","marker"]),
            DictMask(["bgp_message","length"]),
            DictMask(["bgp_message","withdrawn_routes_length"]),
            DictMask(["bgp_message","path_attributes_length"]),
            DictMask(["bgp_message","path_attributes","length"]),
        ])
        mrt_dict_list = cls.read_mrt(path)
        ret_list = []
        for mrt_dict in mrt_dict_list:
            if retrieve_key(mrt_dict["type"]) in {16,17} and retrieve_key(mrt_dict["subtype"]) in {1,4}:
                # type 16: BGP4MP
                # type 17: BGP4MP_ET
                # subtype 1: BGP4MP_MESSAGE
                # subtype 4: BGP4MP_MESSAGE_AS4
                if "bgp_message" not in mrt_dict:
                    # In this case the message is too malformed to be dumped.
                    continue
                msg = mrt_dict["bgp_message"]
                if retrieve_key(msg["type"]) == 2:
                    # The message is an UPDATE message.
                    processed_dict = mask_dict(mrt_dict, dict_mask_set)
                    ret_list.append(processed_dict)
        return ret_list
    
    @classmethod
    def get_route_info(cls, path):
        """
        Return a list of RouteInfo, each represents an entry in the routing table.
        Used to analyze RIB MRT files.
        Have to deal with the repeated items in the MRT file.
        
        `path`: indicates the path to the MRT file.
        """
        mrt_dict_list = cls.read_mrt(path)
        ret_list = []
        for mrt_dict in mrt_dict_list:
            if retrieve_key(mrt_dict["subtype"]) in {2}:
                as_path = []
                next_hop = ""
                announced = f"{mrt_dict["prefix"]}/{mrt_dict["length"]}"
                try:
                    for rib_entry in mrt_dict["rib_entries"]:
                        for attribute in rib_entry["path_attributes"]:
                            if retrieve_key(attribute["type"]) == 2:
                                # type 2: AS_PATH attribute
                                for seg in attribute["value"]:
                                    as_path = as_path + [int(asn) for asn in seg["value"]]
                            elif retrieve_key(attribute["type"]) == 3:
                                # type 3: NEXT_HOP attribute
                                next_hop = attribute["value"]

                except KeyError:
                    pass

                route_info = RouteInfo(
                    as_path=as_path,
                    next_hop=next_hop,
                    announced=announced
                )
                
                if route_info not in ret_list:
                    ret_list.append(route_info)
        
        return ret_list

    @classmethod
    def get_update_message_info(cls, path):
        """
        Return a list of UpdateMessageInfo, each represents an Update message received.
        Used to analyze message MRT files.
        
        `path`: indicates the path to the MRT file.
        """
        mrt_dict_list = cls.read_mrt(path)
        ret_list = []
        for mrt_dict in mrt_dict_list:
            if retrieve_key(mrt_dict["type"]) in {16,17} and retrieve_key(mrt_dict["subtype"]) in {1,4}:
                # type 16: BGP4MP
                # type 17: BGP4MP_ET
                # subtype 1: BGP4MP_MESSAGE
                # subtype 4: BGP4MP_MESSAGE_AS4
                msg = mrt_dict["bgp_message"]

                if retrieve_key(msg["type"]) == 2:
                    # type 2: UPDATE message
                    as_path = []
                    next_hop = ""
                    announced = []
                    withdrawn = []
                    try:
                        for attribute in msg["path_attributes"]:
                            if retrieve_key(attribute["type"]) == 2:
                                # type 2: AS_PATH attribute
                                for seg in attribute["value"]:
                                    as_path = as_path + [int(asn) for asn in seg["value"]]
                            elif retrieve_key(attribute["type"]) == 3:
                                # type 3: NEXT_HOP attribute
                                next_hop = attribute["value"]
                            elif retrieve_key(attribute["type"]) == 14:
                                # type 14: MP_REACH_NLRI attribute
                                nlri_list = attribute["value"]["nlri"]
                                for nlri in nlri_list:
                                    prefix = f"{nlri["prefix"]}/{nlri["length"]}"
                                    if prefix not in announced:
                                        announced.append(prefix)
                            elif retrieve_key(attribute["type"]) == 15:
                                # type 15: MP_UNREACH_NLRI attribute
                                wroute_list = attribute["value"]["withdrawn_routes"]
                                for wroute in wroute_list:
                                    prefix = f"{wroute["prefix"]}/{wroute["length"]}"
                                    if prefix not in withdrawn:
                                        withdrawn.append(prefix)
                        nlri_list = msg["nlri"]
                        for nlri in nlri_list:
                            prefix = f"{nlri["prefix"]}/{nlri["length"]}"
                            if prefix not in announced:
                                announced.append(prefix)
                        wroute_list = msg["withdrawn_routes"]
                        for wroute in wroute_list:
                            prefix = f"{wroute["prefix"]}/{wroute["length"]}"
                            if prefix not in withdrawn:
                                withdrawn.append(prefix)
                    except KeyError:
                        pass

                    update_message_info = UpdateMessageInfo(
                        from_as=int(mrt_dict["peer_as"]),
                        to_as=int(mrt_dict["local_as"]),
                        as_path=as_path,
                        next_hop=next_hop,
                        announced=announced,
                        withdrawn=withdrawn,
                    )
                    ret_list.append(update_message_info)

        return ret_list
