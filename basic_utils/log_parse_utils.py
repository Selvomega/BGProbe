"""
This module provides the functions used to parse the log files.
"""

import mrtparse, json, ipaddress, re
from abc import abstractmethod

def prefix_comp(pref_1: str, pref_2: str) -> bool:
    """
    Compare if two prefixes are equivalent.
    For example, 10.0.0.1/24 and 10.0.0.127/24 are equivalent.
    The input prefix must be of the form "x.x.x.x/x"
    """
    try:
        net1 = ipaddress.IPv4Network(pref_1, strict=False)
        net2 = ipaddress.IPv4Network(pref_2, strict=False)
        return net1 == net2
    except ValueError:
        raise ValueError(f"Invalid prefix format ({pref_1}, {pref_2}). Must be like 'x.x.x.x/x'.")

def retrieve_val(entry: dict):
    """
    Retrieve the value from a dict variable with only 1 entry.
    Will first check the number of entries of the dictionary.
    """
    assert len(entry)==1
    return next(iter(entry.values()))

def retrieve_key(entry: dict):
    """
    Retrieve the key from a dict variable with only 1 entry.
    Will first check the number of entries of the dictionary.
    """
    assert len(entry)==1
    return next(iter(entry))

class MRTEngine:
    """
    The engine used to parse the MRT file
    """
    @classmethod
    @abstractmethod
    def exist_route(cls, path: str, input_prefix: str) -> bool:
        """Check if the route to the input prefix exists."""
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def exist_update_prefix(cls, path: str, input_prefix: str) -> bool:
        """Check if the UPDATE message advertising the prefix exist."""
        raise NotImplementedError()

class MrtparseEngine(MRTEngine):
    """
    MRTEngine supported by mrtparse
    """
    @classmethod
    def read_mrt(cls, path: str):
        """
        Read the MRT file and return the results.
        """
        reader = mrtparse.Reader(open(path, "rb"))
        ret_list = []
        for entry in reader:
            ret_list.append(entry.data)
        return ret_list

    @classmethod
    def exist_route(cls, path: str, input_prefix: str) -> bool:
        """
        Check if the route to the input prefix exists
        """
        mrt_list = cls.read_mrt(path)
        for item in mrt_list:
            # if retrieve_val(item["type"]) in {"TABLE_DUMP", "TABLE_DUMP_V2"} and retrieve_val(item["subtype"]) == "RIB_IPV4_UNICAST":
            try:
                if retrieve_key(item["type"]) in {12, 13} and retrieve_key(item["subtype"]) == 2:
                    # type 12: TABLE_DUMP
                    # type 13: TABLE_DUMP_V2
                    # subtype 2: RIB_IPV4_UNICAST
                    route_prefix = f"{item["prefix"]}/{item["length"]}"
                    if prefix_comp(input_prefix, route_prefix):
                        return True
            except KeyError:
                continue
        return False

    @classmethod
    def exist_update_prefix(cls, path: str, input_prefix: str):
        """
        Check if the UPDATE message advertising the prefix exist.
        """
        mrt_list = cls.read_mrt(path)
        for item in mrt_list:
            try:
                if retrieve_key(item["type"]) in {16,17} and retrieve_key(item["subtype"]) in {1,4}:
                    # type 16: BGP4MP
                    # type 17: BGP4MP_ET
                    # subtype 1: BGP4MP_MESSAGE
                    # subtype 4: BGP4MP_MESSAGE_AS4
                    msg = item["bgp_message"]
                    if retrieve_key(msg["type"]) == 2:
                        # type 2: UPDATE message
                        # Start to check if the prefix is anounced in the message
                        
                        # First check the NLRI field
                        nlri = msg["nlri"]
                        for pref_dict in nlri:
                            prefix = f"{pref_dict["prefix"]}/{pref_dict["length"]}"
                            if prefix_comp(prefix, input_prefix):
                                return True
                        # Then check the MP_REACH_NLRI field
                        for attr in msg["path_attributes"]:
                            if retrieve_key(attr["type"]) == 14:
                                attr_val = attr["value"]
                                if retrieve_key(attr_val["afi"])==retrieve_key(attr_val["safi"])==1:
                                    nlri = attr_val["nlri"]
                                    for pref_dict in nlri:
                                        prefix = f"{pref_dict["prefix"]}/{pref_dict["length"]}"
                                        if prefix_comp(prefix, input_prefix):
                                            return True
            except KeyError:
                continue
        return False

class ExaBGPLogEngine:
    """
    The engine used to parse the ExaBGP log.
    """
    @classmethod
    def extract_update_json_blocks(cls, path: str) -> list[dict]:
        """
        Extract from the ExaBGP log the json content 'decoded UPDATE (...) json { ... }' 
        and convert to Python dictionary.
        """
        update_jsons = []
        pattern = re.compile(r'decoded UPDATE\s+\(\s*\d+\s*\)\s+json\s+{', re.IGNORECASE)

        with open(path, 'r') as file:
            log = file.read()
        
        lines = log.strip().splitlines()
        inside_json = False
        brace_level = 0
        json_lines = []

        for line in lines:
            if not inside_json:
                if pattern.search(line):
                    inside_json = True
                    start_idx = line.find('{')
                    json_fragment = line[start_idx:]
                    brace_level = json_fragment.count('{') - json_fragment.count('}')
                    json_lines = [json_fragment]
                    if brace_level == 0:
                        json_str = "\n".join(json_lines)
                        try:
                            update_jsons.append(json.loads(json_str))
                        except json.JSONDecodeError as e:
                            print(f"Parse failed: {e}")
                        inside_json = False
                        json_lines = []
            else:
                json_lines.append(line)
                brace_level += line.count('{') - line.count('}')
                if brace_level == 0:
                    json_str = "\n".join(json_lines)
                    try:
                        update_jsons.append(json.loads(json_str))
                    except json.JSONDecodeError as e:
                        print(f"Parse failed: {e}")
                    inside_json = False
                    json_lines = []

        return update_jsons

    @classmethod
    def exist_update_prefix(cls, path: str, input_prefix: str):
        """
        Check if the ExaBGP client has received an UPDATE .
        """
        update_jsons = cls.extract_update_json_blocks(path)
        for update_json in update_jsons:
            try:
                update_msg = update_json["neighbor"]["message"]["update"]
                ipv4_unicast_announce : dict = update_msg["announce"]["ipv4 unicast"]
                for value_list in ipv4_unicast_announce.values():
                    for value in value_list:
                        if "nlri" in value and prefix_comp(value["nlri"], input_prefix):
                            return True
            except KeyError:
                continue
        return False
    
    @classmethod
    def exist_invalid(cls, path: str):
        """
        Check if the ExaBGP log has reported any invalid or errorneous message.
        """
        with open(path, 'r') as file:
            log = file.read()
            return "invalid" in log.lower() or "error" in log.lower()

if __name__ == "__main__":
    path = "/home/xinpeilin/BGProbe/data/test_single/testcase-29_2025-05-19_15-38-17/messages.mrt"
    path = "/home/xinpeilin/BGProbe/data/test_single/testcase-2_2025-05-11_16-56-00/messages.mrt"
    path = "/home/xinpeilin/BGProbe/data/test_single/testcase-20_2025-05-13_14-14-31/messages.mrt"
    path = "/home/xinpeilin/BGProbe/data/test_single/testcase-20_2025-05-13_14-14-31/exabgp.log"
    # path = "/home/xinpeilin/BGProbe/data/test_single/testcase-2_2025-05-19_21-18-27/exabgp.log"

    # ret = read_mrt(path)
    # for item in ret:
    #     print(json.dumps(item, indent=2))
    #     # print(type(item["subtype"]))
    #     # print(retrieve_val(item["subtype"])=="PEER_INDEX_TABLE")
    #     # for a in item["subtype"]:
    #     #     print(a)

    # print(MrtparseEngine.exist_update_prefix(path, "59.66.130.0/24"))
    # print(json.dumps(ExaBGPLogEngine.extract_update_json_blocks(path)[0], indent=2))
    print(ExaBGPLogEngine.exist_update_prefix(path, "59.66.130.1/24"))
