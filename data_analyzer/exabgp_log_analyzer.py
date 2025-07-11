import re, json
from .basic_types import UpdateMessageInfo, ExaBGPLogInfo
from .utils import *
from basic_utils.file_utils import read_file

class ExaBGPLogAnalyzer:
    """
    The analyzer of ExaBGP log file.
    """
    
    @classmethod
    def extract_update_message(cls, path: str):
        """
        Extract from the ExaBGP log the update message content and convert to python string.
        """
        pass

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
    def get_exabgp_log_data(cls, path: str) -> dict:
        """
        Return a dict representing the corresponding information in the ExaBGPs log.
        """
        dict_mask_set = DictMaskSet([
            DictMask(["exabgp"]),
            DictMask(["time"]),
            DictMask(["host"]),
            DictMask(["pid"]),
            DictMask(["ppid"]),
            DictMask(["counter"]),
            DictMask(["type"]),
        ])
        update_json_blocks = cls.extract_update_json_blocks(path)
        update_message_list = []
        for update_dict in update_json_blocks:
            processed_dict = mask_dict(update_dict,dict_mask_set)
            update_message_list.append(processed_dict)
        ret_dict = {
            "invalid": "invalid" in read_file(path=path).lower(),
            "update_messages": update_message_list
        }
        return ret_dict
    
    @classmethod
    def get_exabgp_log_info(cls, path: str) -> ExaBGPLogInfo:
        """
        Return an ExaBGPLogInfo, representing the corresponding information in the ExaBGPs log.
        """
        update_info_list = []
        update_list = cls.extract_update_json_blocks(path)
        for update in update_list:
            update_core = update["neighbor"]["message"]["update"]
            as_path = []
            next_hop = ""
            announced = []
            withdrawn = []
            try:
                as_path = update_core["attribute"]["as-path"]
            except KeyError:
                pass
            try:
                next_hop = retrieve_key(retrieve_val(update_core["announce"]))
            except KeyError:
                pass
            try:
                for item in retrieve_val(retrieve_val(update_core["announce"])):
                    prefix = retrieve_val(item)
                    if prefix not in announced:
                        announced.append(prefix)
            except KeyError:
                pass
            try:
                for item in retrieve_val(update_core["withdraw"]):
                    prefix = retrieve_val(item)
                    if prefix not in withdrawn:
                        withdrawn.append(prefix)
            except KeyError:
                pass
            update_message_info = UpdateMessageInfo(
                from_as=update["neighbor"]["asn"]["peer"],
                to_as=update["neighbor"]["asn"]["local"],
                as_path=as_path,
                next_hop=next_hop,
                announced=announced,
                withdrawn=withdrawn
            )
            update_info_list.append(update_message_info)
        exabgp_log_info = ExaBGPLogInfo(
            invalid="invalid" in read_file(path=path).lower(),
            update_messages=update_info_list
        )
        return exabgp_log_info

    # TODO: support more IP type in this function. 
    @classmethod
    def if_exist_update_prefix(cls, path: str, input_prefix: str):
        """
        Check if the ExaBGP client has received an UPDATE announcing given prefix.
        """
        exabgp_log_info : ExaBGPLogInfo = cls.get_exabgp_log_info(path)
        for update_message_info in exabgp_log_info.update_messages:
            for prefix in update_message_info.announced:
                if prefix_comp(prefix, input_prefix):
                    return True
        return False
    
    @classmethod
    def if_exist_withdraw_prefix(cls, path: str, input_prefix: str):
        """
        Check if the ExaBGP client has received an UPDATE announcing given prefix.
        """
        exabgp_log_info : ExaBGPLogInfo = cls.get_exabgp_log_info(path)
        for update_message_info in exabgp_log_info.update_messages:
            for prefix in update_message_info.withdrawn:
                if prefix_comp(prefix, input_prefix):
                    return True
        return False

    @classmethod
    def if_exist_invalid(cls, path: str):
        """
        Check if the ExaBGP log has reported any invalid or errorneous message.
        """
        exabgp_log_info : ExaBGPLogInfo = cls.get_exabgp_log_info(path)
        return exabgp_log_info.invalid
