from .binary_field_node import BinaryFieldNode
from basic_utils.binary_utils import num2bytes, bytes2num
from network_utils.utils import is_valid_ipv4, is_valid_ipv4_prefix, get_ip_segments, get_ipv4_prefix_parts
import numpy as np
import random
from abc import abstractmethod

class Number_BFN(BinaryFieldNode):
    """
    The field representing a number.
    """
    def __init__(self,
                 num_val: int,
                 num_len: int = 1):
        
        ###### Basic attributes ######

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(Number_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        self.num_val = num_val
        self.num_len = num_len

    @classmethod
    @abstractmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        raise NotImplementedError()

    ########## Get binary info ##########

    def get_binary_expression_inner(self):
        """Get binary expression."""
        return num2bytes(self.num_val, self.num_len)
    
    ########## Update according to dependencies ##########
    
    def update_on_dependencies_inner(self):
        """
        Update the current BFN according to its dependencies.
        This BFN do not have dependencies.
        """
        # You should not raise error because of `attach` function
        return

    ########## Methods for generating random mutation ##########

    def random_num(self) -> int:
        """
        Return a random number value.
        """
        byte_seq = random.randbytes(self.num_len)
        return bytes2num(byte_seq)

    ########## Methods for applying mutation ##########

    @BinaryFieldNode.set_function_decorator
    def set_num(self, num_val: int):
        """
        Set the number value of current BFN.
        """
        self.num_val = num_val

    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set + [
        BinaryFieldNode.MutationItem(random_num, set_num)
    ]

class Length_BFN(Number_BFN):
    """
    The length field.
    """
    def __init__(self,
                 length_val : int,
                 length_byte_len : int = 1,
                 include_myself : bool = False):
        """Initialize the length BFN."""

        ###### Basic attributes ######

        super().__init__(num_val=length_val, num_len=length_byte_len)

        ###### Set the weights ######
        self.weights = np.ones(len(Length_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        # `num_val` and `num_len` has been defined in `Number_BFN`.
        # If the length should consider the length field itself.
        self.include_myself = include_myself
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "Length_BFN"
    
    ########## Get binary info ##########

    # Defined in `Number_BFN`

    ########## Update according to dependencies ##########
    
    def update_on_dependencies_inner(self):
        """
        Update the current BFN according to its dependencies.
        Calculate the sum of length of the dependency fields.
        """
        len_sum = self.num_len if self.include_myself else 0
        for dependency in self.dependencies.values():
            len_sum = len_sum + dependency.get_binary_length()
        self.num_val = len_sum

    ########## Methods for generating random mutation ##########
    
    def random_length(self) -> int:
        """
        Return a random length fitting in `self.num_len` bytes.
        Just an encapsulation of the father class' method. 
        """
        return self.random_num()

    ########## Methods for applying mutation ##########

    def set_length(self, length_val: int):
        """
        Set the length_val of current BFN.
        Just an encapsulation of the father class' method. 
        So there is NO decorator. 
        """
        self.set_num(length_val)
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = Number_BFN.mutation_set


class ASN_BFN(Number_BFN):
    """
    The AS number field.
    """
    def __init__(self,
                 asn: int,
                 asn_byte_len=2):
        """Initialize the ASN BFN."""

        ###### Basic attributes ######

        super().__init__(num_val=asn, num_len=asn_byte_len)

        ###### Set the weights ######
        self.weights = np.ones(len(ASN_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        # No special attributes
        # Defined in `Number_BFN`
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "ASN_BFN"
    
    ########## Get binary info ##########

    # Defined in `Number_BFN`

    ########## Update according to dependencies ##########
    
    # Defined in `Number_BFN`

    ########## Methods for generating random mutation ##########

    def random_asn(self) -> int:
        """
        Return a random AS number.
        Just an encapsulation of the father class' method. 
        """
        return self.random_num()

    def random_legal_asn(self) -> int:
        """
        Return a random AS number.
        The AS numbr is guaranteed to be legal.
        """
        if self.num_len == 2:
            return random.randint(1,64495)
        elif self.num_len == 4:
            return random.randint(65536, 4199999999)
        else:
            # You are using an illegal AS number length
            # Do not care whether the result is legal now.
            byte_seq = random.randbytes(self.asn_byte_len)
            return bytes2num(byte_seq)
    
    # To be checked. 
    def random_short_asn(self) -> int:
        """
        Random short AS number.
        Normally a short asn should not be used in long ASN expression.
        """
        return random.randint(1,64495)

    ########## Methods for applying mutation ##########

    def set_asn(self, asn: int):
        """
        Set the ASN of current BFN.
        Just an encapsulation of the father class' method. 
        So there is NO decorator. 
        """
        self.set_num(asn)

    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = Number_BFN.mutation_set + [
        BinaryFieldNode.MutationItem(random_legal_asn, set_asn),
        BinaryFieldNode.MutationItem(random_short_asn, set_asn)
    ]

class IPv4Address_BFN(BinaryFieldNode):
    """
    The IPv4 address field.
    """
    def __init__(self,
                 ip_addr: str):
        """Initialize the IPv4 address BFN."""
        
        if not is_valid_ipv4(ip_addr):
            raise ValueError(f"Please enter a valid IPv4 address (Your input: {ip_addr})")

        ###### Basic attributes ######

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(IPv4Address_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        self.ip_addr = ip_addr

    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "IPv4Address_BFN"
    
    ########## Get binary info ##########

    def get_binary_expression_inner(self):
        """Get binary expression."""
        segments = get_ip_segments(self.ip_addr)
        return b''.join([
            num2bytes(segment,1) for segment in segments
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

    def random_ip_addr(self) -> str:
        """
        Return a random IPv4 address.
        """
        byte_seq = [random.randbytes(1) for _ in range(0,4)]
        int_seq = [bytes2num(byte_elem) for byte_elem in byte_seq]
        ip_addr = '.'.join([str(num) for num in int_seq])
        return ip_addr

    ########## Methods for applying mutation ##########

    @BinaryFieldNode.set_function_decorator
    def set_ip_addr(self, ip_addr: str):
        """
        Set the IPv4 address of current BFN.
        """
        if not is_valid_ipv4(ip_addr):
            raise ValueError(f"Please enter a valid IPv4 address (Your input: {ip_addr})")
        self.ip_addr = ip_addr
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set + [
        BinaryFieldNode.MutationItem(random_ip_addr, set_ip_addr)
    ]

class IPv4PrefixValue_BFN(BinaryFieldNode):
    """
    The IPv4 prefix value field.
    """
    def __init__(self,
                 ip_addr: str):
        """Initialize the IPv4 prefix BFN."""
        
        if not is_valid_ipv4_prefix(ip_addr):
            raise ValueError(f"Please enter a valid IPv4 prefix (Your input: {ip_addr})")

        ###### Basic attributes ######

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(IPv4PrefixValue_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        ip_part, prefix_length = get_ipv4_prefix_parts(ip_addr)
        self.ip_addr = ip_part
        self.prefix_len = prefix_length
        self.segment_num = (self.prefix_len+7) // 8
        self.padding_bits = [0]*(self.segment_num*8-self.prefix_len)

    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "IPv4PrefixValue_BFN"

    ########## Get binary info ##########

    def get_binary_expression_inner(self):
        """
        Get binary expression.
        Only preserve the 
        """
        segments = get_ip_segments(self.ip_addr)
        segment_res = 8 - len(self.padding_bits)
        segment_list = segments[:self.segment_num].copy()
        if len(segment_list)>=1:
            # Compute the valid part of the IP address.
            base = 2**8
            comp = 0
            for i in range(0,segment_res):
                base = base>>1
                comp = comp | base
            segment_list[-1] = segment_list[-1]&comp
            # Compute the padding part of the IP address.
            comp = 0
            for bit in self.padding_bits:
                comp = comp<<1
                comp = comp | bit
            segment_list[-1] = segment_list[-1]|comp
        return b''.join([
            num2bytes(segment,1) for segment in segment_list
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

    def random_ip_addr(self) -> str:
        """
        Return a random IPv4 address.
        """
        byte_seq = [random.randbytes(1) for _ in range(0,4)]
        int_seq = [bytes2num(byte_elem) for byte_elem in byte_seq]
        ip_addr = '.'.join([str(num) for num in int_seq])
        return ip_addr
    
    def random_padding_bits(self) -> list[int]:
        """
        Return a random padding bit list.
        """
        return [random.randint(0,1) for _ in self.padding_bits]

    def random_prefix_len(self) -> int:
        """
        Return a random prefix length.
        """
        return random.randint(0,32)

    ########## Methods for applying mutation ##########

    @BinaryFieldNode.set_function_decorator
    def set_ip_addr(self, ip_addr: str):
        """
        Set the IPv4 address of current BFN.
        """
        if not is_valid_ipv4(ip_addr):
            raise ValueError(f"Please enter a valid IPv4 address (Your input: {ip_addr})")
        self.ip_addr = ip_addr
    
    @BinaryFieldNode.set_function_decorator
    def set_padding_bits(self, padding_bits: list[int]):
        """
        Set the padding bits of current BFN.
        """
        if len(padding_bits) != len(self.padding_bits):
            raise ValueError(f"The input padding bit list must have the same length with the current one.")
        if any(bit not in (0, 1) for bit in padding_bits):
            raise ValueError(f"The input padding bit list must only contain 0 or 1.")
        self.padding_bits = padding_bits
    
    @BinaryFieldNode.set_function_decorator
    def set_prefix_len(self, prefix_len: int):
        """
        Set the prefix length of current BFN.
        """
        if prefix_len<0 or prefix_len>32:
            raise ValueError("The input length must be in [0,32]")
        self.prefix_len = prefix_len
        self.segment_num = (self.prefix_len+7) // 8
        self.padding_bits = [0]*(self.segment_num*8-self.prefix_len)
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set + [
        BinaryFieldNode.MutationItem(random_ip_addr, set_ip_addr),
        BinaryFieldNode.MutationItem(random_padding_bits, set_padding_bits),
        BinaryFieldNode.MutationItem(random_prefix_len, set_prefix_len)
    ]

class IPv4PrefixLength_BFN(Length_BFN):
    """
    The IPv4 prefix length field.
    """
    def __init__(self,
                 length_val: int):
        """
        Initialize the IPv4 prefix length BFN
        """

        ###### Basic attributes ######

        super().__init__(length_val=length_val,
                         length_byte_len=1,
                         include_myself=False)

        ###### Set the weights ######
        self.weights = np.ones(len(IPv4PrefixLength_BFN.mutation_set))
        self.weights /= np.sum(self.weights)
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "IPv4PrefixLength_BFN"

    ######### Update according to dependencies ##########
    
    def update_on_dependencies_inner(self):
        """
        Update the current BFN according to its dependencies.
        The num_val is set to the length of the prefix.
        """
        dependency: IPv4PrefixValue_BFN = self.dependencies[f"{IPv4PrefixValue_BFN.get_bfn_name()}_0"]
        self.num_val = dependency.prefix_len
    
class IPv4Prefix_BFN(BinaryFieldNode):
    """
    The full IPv4 prefix field.
    """
    def __init__(self,
                 prefix_val_bfn: IPv4PrefixValue_BFN,
                 prefix_len_bfn: IPv4PrefixLength_BFN):
        """Initialize the full IPv4 prefix field."""
        
        ###### Basic attributes ######

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(IPv4Prefix_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        # No special attributes

        ###### Deal with relations with and between children ######

        # Initialize the children. 
        # The sequence is very important.
        # Parents can still be `None`
        self.prefix_len_key  = self.append_child(prefix_len_bfn)
        self.prefix_val_key = self.append_child(prefix_val_bfn)
        # Update the detach state of the current BFN.
        self.detach_according_to_children()
        # Add dependencies between children
        self.add_dependency_between_children(dependent_key=self.prefix_len_key,
                                             dependency_key=self.prefix_val_key)
        # Let children update
        self.children_update()
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "IPv4Prefix_BFN"

    ########## Factory methods: Create an instance of the class ##########

    @classmethod
    def get_bfn(cls, ip_prefix: str):
        """
        Get the IPv4 prefix BFN from the ip prefix string.
        """
        if not is_valid_ipv4_prefix(ip_prefix):
            raise ValueError("The input must be a valid IPv4 prefix like \"xx.xx.xx.xx/xx\"")
        _, prefix_len = get_ipv4_prefix_parts(ip_prefix)
        return IPv4Prefix_BFN(prefix_val_bfn=IPv4PrefixValue_BFN(ip_prefix),
                              prefix_len_bfn=IPv4PrefixLength_BFN(prefix_len))
    
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

    def set_prefix_len_len(self, length: int):
        """
        Set the value of the prefix length field. 
        """
        bfn: IPv4PrefixLength_BFN = self.children[self.prefix_len_key]
        bfn.set_length(length)
    
    def set_prefix_val_len(self, length: int):
        """
        Set the prefix length of the prefix value field. 
        """
        bfn: IPv4PrefixValue_BFN = self.children[self.prefix_val_key]
        bfn.set_prefix_len(length)
    
    def set_ip_addr(self, ip_addr: str):
        """
        Set the ip address of the prefix value field. 
        """
        bfn: IPv4PrefixValue_BFN = self.children[self.prefix_val_key]
        bfn.set_ip_addr(ip_addr)
    
    def set_padding_bits(self, padding_bits: list[int]):
        """
        Set the padding bit list of the prefix value field.
        """
        bfn: IPv4PrefixValue_BFN = self.children[self.prefix_val_key]
        bfn.set_padding_bits(padding_bits)
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set

class BinaryFieldList_BFN(BinaryFieldNode):
    """
    A list of BinaryFieldNode.
    All BFNs must have the same type.
    """

    def __init__(self,
                 bfn_list : list[BinaryFieldNode],
                 list_element_name : str,
                 BFN_type_check: bool = True):
        """Initialize the IPv4 address BFN."""

        ###### Basic attributes ######

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(BinaryFieldList_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        self.BFN_type_check = BFN_type_check

        # Check all BFNs in the input list are of the same 
        for bfn in bfn_list:
            if self.BFN_type_check and bfn.get_bfn_name() != list_element_name:
                raise ValueError(f"The input list of BFNs must contain name consistent with `list_element_name`!")

        self.list_element_name : str = list_element_name
        self.bfn_list : list[BinaryFieldNode] = bfn_list

        ###### Deal with relations with and between children ######

        # Initialize the children. 
        # The sequence is very important.
        # Parents can still be `None`
        for bfn in self.bfn_list:
            self.append_child(bfn)
        # Update the detach state of the current BFN.
        self.detach_according_to_children()
    
    # This is NOT a `classmethod`!
    def get_bfn_name(self) -> str:
        """Get the name of the BFN."""
        return f"BinaryFieldList_BFN__{self.list_element_name}__"

    def get_list_len(self) -> int:
        """Get the number of elements in the BFN list."""
        return len(self.bfn_list)
    
    ########## Get binary info ##########

    def get_binary_expression_inner(self):
        """Get binary expression."""
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
    
    # Defined in `BinaryFieldNode`

    ########## Methods for applying mutation ##########

    @BinaryFieldNode.set_function_decorator
    def append_bfn(self, bfn: BinaryFieldNode):
        """
        Append a BFN to the current BFN.
        """
        if self.BFN_type_check and self.list_element_name != bfn.get_bfn_name():
            # The type of BFN do not match
            raise ValueError(f"The type of input BFN ({bfn.get_bfn_name()}) cannot match the type of BFNs in the BFN list ({self.list_element_name}).")
        self.bfn_list.append(bfn)
        self.append_child(bfn)
    
    def set_bfn_list(self, bfn_list: list[BinaryFieldNode]):
        """
        Reset the BFN list.
        """
        for bfn in bfn_list:
            if self.BFN_type_check and bfn.get_bfn_name() != self.list_element_name:
                raise ValueError(f"The input list of BFNs must contain name consistent with `list_element_name`!")
        self.bfn_list : list[BinaryFieldNode] = bfn_list
        # Clear the original children dictionary
        for child in self.children.values():
            child.parent = None
        self.children.clear()
        # Initialize the children.
        for bfn in self.bfn_list:
            self.append_child(bfn)
        # Update the detach state of the current BFN.
        self.detach_according_to_children()

    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set

class Reserved_BFN(BinaryFieldNode):
    """
    Reserved field BFN.
    """
    def __init__(self,
                 reserved_val: bytes = None):
        """Initialize the reserved BFN"""

        ###### Redefine default input parameters to avoid shallow-copy ######

        if reserved_val is None:
            reserved_val = b'\x00'
        
        ###### Basic attributes ######

        super().__init__()

        ###### Set the weights ######
        self.weights = np.ones(len(Reserved_BFN.mutation_set))
        self.weights /= np.sum(self.weights)

        ###### special attributes ######

        self.reserved_val : bytes = reserved_val
    
    @classmethod
    def get_bfn_name(cls) -> str:
        """Get the name of the BFN."""
        return "Reserved_BFN"

    ########## Get binary info ##########

    def get_binary_expression_inner(self) -> bytes:
        """Get binary expression."""
        return self.reserved_val
    
    ########## Update according to dependencies ##########
    
    def update_on_dependencies_inner(self):
        """
        Update the current BFN according to its dependencies.
        This BFN do not have dependencies.
        """
        # You should not raise error because of `attach` function
        return

    ########## Methods for generating random mutation ##########
    
    def random_reserved_val(self) -> bytes:
        """
        Return a random reserved BFN value.
        The length of the newly generated value is still the same as the previous one
        """
        return random.randbytes(len(self.reserved_val))
    
    ########## Methods for applying mutation ##########

    @BinaryFieldNode.set_function_decorator
    def set_reserved_val(self,reserved_val: bytes):
        """
        Set the reserved value.
        """
        self.reserved_val = reserved_val
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set + [
        BinaryFieldNode.MutationItem(random_reserved_val,set_reserved_val)
    ]
