import ipaddress, re, copy
from typing import Callable

def prefix_comp(pref_1: str, pref_2: str, is_ipv4=True) -> bool:
    """
    Compare if two prefixes are equivalent.
    For example, 10.0.0.1/24 and 10.0.0.127/24 are equivalent.

    `is_ipv4`: Indicate if you want to compare ipv4 prefixes. `False` to compare ipv6 prefixes.
    """
    try:
        if is_ipv4:
            net1 = ipaddress.IPv4Network(pref_1, strict=False)
            net2 = ipaddress.IPv4Network(pref_2, strict=False)
        else:
            net1 = ipaddress.IPv6Network(pref_1, strict=False)
            net2 = ipaddress.IPv6Network(pref_2, strict=False)
        return net1 == net2
    except ValueError:
        raise ValueError(f"Invalid prefix format ({pref_1}, {pref_2}).")

def prefix_match(content: str, is_ipv4: bool = True):
    """
    Match the first IP prefix in the string.

    `is_ipv4`: Indicate if you want to match an ipv4 prefix. False to match ipv6.

    Returns the matched prefix as a string, or None if not found.
    """
    if is_ipv4:
        # IPv4 CIDR: e.g., 192.168.0.0/24
        pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}/\d{1,2}\b'
    else:
        # IPv6 CIDR regex that matches full and shorthand formats (e.g., 2001:db8::/32)
        pattern = (
            r'\b('
            r'(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}'               # full form
            r'|(?:[0-9a-fA-F]{1,4}:){1,7}:'                           # :: suffix form
            r'|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}'           # :: in middle
            r'|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}'
            r'|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}'
            r'|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}'
            r'|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}'
            r'|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})'
            r'|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)'                    # :: prefix form
            r')/\d{1,3}\b'
        )

    match = re.search(pattern, content)
    return match.group(0) if match else None

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

def set_comp(item1, item2) -> bool:
    """
    Convert the two inputs into Python set and compare.
    """
    return set(item1) == set(item2)

class DictMask:
    """
    This class stores a list of keys for a recursive dictionary data structure.
    It is used to indicate the key-value pairs should be masked in the recursive data structure.
    """
    def __init__(self, key_list: list, mask_func: Callable = lambda x: True):
        """
        Initialize the DictMask.
        `mask_func` is used judge if the value should be masked.
        """
        self.key_list = key_list
        self.mask_func = mask_func

    def __str__(self):
        return f"{self.key_list}"

    def copy(self) -> "DictMask":
        return copy.deepcopy(self)
    
    def is_empty(self) -> bool:
        """
        Return if the DictMask is empty.
        """
        return len(self.key_list) == 0

    def peek(self):
        """
        Return the first layer mask (retrun None if not exist) 
        """
        if not self.is_empty():
            return self.key_list[0]
        else:
            return None
    
    def is_last_layer(self) -> bool:
        """
        Return if the DictMask only have the last layer left.
        """
        return len(self.key_list) == 1
    
    def append(self, key):
        """
        Append a key to the DictMask.
        """
        self.key_list.append(key)
    
    def pop(self):
        """
        Remove the first layer of the key mask.
        """
        if not self.is_empty():
            self.key_list = self.key_list[1:]
    
    def if_include(self, other: "DictMask") -> bool:
        """
        Check if the current DictMask include the other one.
        """
        if len(self.key_list) > len(other.key_list): 
            return False
        for i in range(0,len(self.key_list)):
            if self.key_list[i] != other.key_list[i]:
                return False
        return True

class DictMaskSet:
    """
    The set of DictMask.
    """
    def __init__(self, input):
        """
        Initialize the DictMaskSet with a data struct containing DictMask which can be converted into Python set.
        """
        self.dict_mask_set = set(input)
        self.simplify()

    def __str__(self):
        return "{" + ", ".join(str(item) for item in self.dict_mask_set) + "}"

    def is_empty(self) -> bool:
        """
        Return if the DictMaskSet is empty.
        """
        return len(self.dict_mask_set) == 0

    def add(self, dict_mask: DictMask):
        """
        Add a DictMask to the DictMaskSet.
        """
        self.dict_mask_set.add(dict_mask)

    def get_subset(self, key) -> "DictMaskSet":
        """
        Reduce the DictMaskSet to a subset by a first-layer key.
        """
        input_set = set()
        for dict_mask in self.dict_mask_set:
            if dict_mask.peek() == key:
                new_dict_mask : DictMask = dict_mask.copy()
                new_dict_mask.pop()
                if not new_dict_mask.is_empty():
                    input_set.add(new_dict_mask)

        return DictMaskSet(input_set)

    def discard(self, elem: DictMask):
        """
        Discard an element from the DictMaskSet.
        """
        self.dict_mask_set.discard(elem)

    def simplify(self):
        """
        Simplify the DictMaskSet (merge the DictMask with inclusion relationship)
        """
        new_set = self.dict_mask_set.copy()
        for dict_mask in self.dict_mask_set:
            for other_dict_mask in self.dict_mask_set:
                if dict_mask != other_dict_mask and dict_mask.if_include(other_dict_mask):
                    new_set.discard(other_dict_mask)
        self.dict_mask_set = new_set

def mask_dict(dict_item: dict, dict_mask_set: DictMaskSet) -> dict:
    """
    Mask a recursive dictionary data structure and return the result data structure.
    The mask cannot be matched will be ignored
    """
    def next_layer_dict(item) -> bool:
        """
        Return if the item is a dict or a list of dict
        """
        if isinstance(item, dict):
            return True
        if isinstance(item, list):
            for elem in item:
                if not isinstance(elem, dict):
                    return False
            return True
        return False
    key_list = list(dict_item.keys())
    ret_dict = {}
    for key in key_list:
        preserve = True
        ret_dict_val = dict_item[key]
        for dict_mask in dict_mask_set.dict_mask_set:
            if dict_mask.peek() == key:
                if not dict_mask.is_last_layer() and not next_layer_dict(ret_dict_val):
                    # The dict_mask is not in its last layer and the corresponding value is not a dictionary.
                    # Illegal mask, ignore it
                    continue
                elif dict_mask.is_last_layer():
                    # Ignore the whole key-value pair
                    if isinstance(ret_dict_val, list) and next_layer_dict(ret_dict_val):
                        # treat the value in an element-wise manner.
                        new_ret_dict_val = []
                        for item in ret_dict_val:
                            masked = dict_mask.mask_func(item)
                            if not masked: new_ret_dict_val.append(item)
                        ret_dict_val = new_ret_dict_val
                        break
                    # treat the value as a whole.
                    preserve = not dict_mask.mask_func(ret_dict_val)
                    break
                else:
                    # Now we must have dict_item[key] is a dict or list containing dicts
                    # For list we must examine if the list contains all dict
                    # We should go recursively 
                    new_dict_mask_set = dict_mask_set.get_subset(key)
                    assert not new_dict_mask_set.is_empty()
                    if isinstance(dict_item[key], dict):
                        ret_dict_val = mask_dict(ret_dict_val,new_dict_mask_set)
                    else:
                        # dict_item[key] is a list containing dicts
                        ret_dict_val = [
                            mask_dict(item,new_dict_mask_set) for item in ret_dict_val
                        ]
                    break
        if preserve: ret_dict[key] = ret_dict_val
    return ret_dict               

def dict_comp(dict1: dict, dict2: dict, mask: DictMaskSet) -> bool:
    """
    Compare two dictionaries.
    When comparing, mask some key-value pairs.
    """
    masked_dict1 = mask_dict(dict1, mask)
    masked_dict2 = mask_dict(dict2, mask)
    return masked_dict1 == masked_dict2

def check_difference(dict1: dict, dict2: dict) -> list:
    """
    Check the differences between two recursive dictionary structure.
    """
    # TODO
    return []
