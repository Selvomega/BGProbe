import subprocess
from .mrt_analyzer_base import BaseMRTAnalyzer
from ..utils import *
from ..basic_types import RouteInfo, UpdateMessageInfo
from basic_utils.file_utils import file_exists

class BGPdumpMRTAnalyzer(BaseMRTAnalyzer):
    """
    MRT analyzer supported by bgpdump.
    """

    @classmethod
    def mrt2txt(cls, path: str):
        """
        Call bgpdump to read the MRT file and return the parsed text
        """
        result = subprocess.run(
            f"bgpdump {path}",
            shell=True, # Use shell to explain the command
            stdout=subprocess.PIPE, # capture standard output
            text=True
        )
        return result.stdout

    @classmethod
    def read_mrt(cls, path: str) -> list[dict]:
        """
        Read the MRT file and return the results.
        The results is a list of dictionaries.
        """
        if not file_exists(path):
            return []
        parsed_text = cls.mrt2txt(path)
        
        entries = []
        current_entry = {}
        current_key = None

        for line in parsed_text.splitlines():
            if not line.strip():
                # Use empty line represent the end of an entry
                if current_entry:
                    entries.append(current_entry)
                    current_entry = {}
                    current_key = None
                continue

            if ":" in line:
                # Use colon to separate
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                current_entry[key] = value
                current_key = key
            elif line.startswith("  ") or line.startswith("\t"):
                # Use indentation to separate
                if current_key:
                    if not isinstance(current_entry.get(current_key), list):
                        current_entry[current_key] = [current_entry[current_key]]
                    current_entry[current_key].append(line.strip())
            else:
                key = line.strip()
                current_entry[key] = []
                current_key = key

        # Process the last entry
        if current_entry:
            entries.append(current_entry)

        return entries
    
    @classmethod
    def get_route_data(cls, path) -> list[dict]:
        """
        Return a list of dict, each represents an entry in the routing table.
        Used to analyze RIB MRT files.
        Have to deal with the repeated items in the MRT file.
        
        `path`: indicates the path to the MRT file.
        """
        dict_mask_set = DictMaskSet([
            DictMask(["TIME"]),
            DictMask(["TYPE"]),
            DictMask(["SEQUENCE"]),
            DictMask(["FROM"]),
            DictMask(["ORIGINATED"]),
        ])
        mrt_dict_list = cls.read_mrt(path)
        ret_list = []
        for mrt_dict in mrt_dict_list:
            processed_dict = mask_dict(mrt_dict, dict_mask_set)
            if processed_dict not in ret_list: ret_list.append(processed_dict)
        return ret_list

    @classmethod
    def get_update_message_data(cls, path: str) -> list[dict]:
        """
        Return a list of dict, each represents an Update message received.
        Used to analyze message MRT files.
        
        `path`: indicates the path to the MRT file.
        """
        dict_mask_set = DictMaskSet([
            DictMask(["TIME"]),
            DictMask(["TYPE"]),
        ])
        mrt_dict_list = cls.read_mrt(path)
        ret_list = []
        for mrt_dict in mrt_dict_list:
            if "TYPE" in mrt_dict and "update" in mrt_dict["TYPE"].lower():
                # If the message is an UPDATE message.
                processed_dict = mask_dict(mrt_dict, dict_mask_set)
                ret_list.append(processed_dict)
        return ret_list

    @classmethod
    def get_route_info(cls, path) -> list[RouteInfo]:
        """
        Return a list of RouteInfo, each represents an entry in the routing table.
        Used to analyze RIB MRT files.
        Have to deal with the repeated items in the MRT file.
        
        `path`: indicates the path to the MRT file.
        """
        mrt_dict_list = cls.read_mrt(path)
        ret_list = []
        for mrt_dict in mrt_dict_list:
            route_info = RouteInfo(
                as_path=list(map(int, mrt_dict["ASPATH"].split())) if "ASPATH" in mrt_dict else [], 
                next_hop=mrt_dict["NEXT_HOP"] if "NEXT_HOP" in mrt_dict else "", 
                announced=mrt_dict["PREFIX"] if "PREFIX" in mrt_dict else "" 
            )
            if route_info not in ret_list:  
                ret_list.append(route_info)
        return ret_list

    @classmethod
    def get_update_message_info(cls, path) -> list[UpdateMessageInfo]:
        """
        Return a list of UpdateMessageInfo, each represents an Update message received.
        Used to analyze message MRT files.
        
        `path`: indicates the path to the MRT file.
        """
        mrt_dict_list = cls.read_mrt(path)
        ret_list = []
        for mrt_dict in mrt_dict_list:
            if "TYPE" in mrt_dict and "update" in mrt_dict["TYPE"].lower():
                update_message_info = UpdateMessageInfo(
                    from_as=int(mrt_dict["FROM"].split()[1][2:]) if "FROM" in mrt_dict else -1,
                    to_as=int(mrt_dict["TO"].split()[1][2:]) if "TO" in mrt_dict else -1,
                    as_path=list(map(int, mrt_dict["ASPATH"].split())) if "ASPATH" in mrt_dict else [],
                    next_hop=mrt_dict["NEXT_HOP"] if "NEXT_HOP" in mrt_dict else "",
                    announced=mrt_dict["ANNOUNCE"] if "ANNOUNCE" in mrt_dict else [],
                    withdrawn=mrt_dict["WITHDRAW"] if "WITHDRAW" in mrt_dict else []
                )
                ret_list.append(update_message_info)
        return ret_list
