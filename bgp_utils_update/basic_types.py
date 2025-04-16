from .binary_field_node import BinaryFieldNode
from data_utils.binary_utils import num2bytes, bytes2num
import numpy as np
import random

class Length_BFN(BinaryFieldNode):
    """
    The length field.
    """
    def __init__(self,
                 length_val : int,
                 length_byte_len : int = 1,
                 include_myself : bool = False):
        """Initialize the length BFN."""

        ###### Basic attributes ######

        self.children : dict[str,BinaryFieldNode] = {}
        self.parent : BinaryFieldNode = None
        self.dependencies = dict[str,BinaryFieldNode] = {}
        self.depend_on_me = dict[str,BinaryFieldNode] = {}
        self.detached = False
        self.binary_content : bytes = None
        self.prefix : bytes = b''
        self.suffix : bytes = b''

        # Initialize all weights to 1.
        # IMPORTANT: use the `mutation_set` of current class!
        self.weights = np.ones(len(Length_BFN.mutation_set))
        # Normalize
        self.weights /= np.sum(self.weights)
        # Set the learning rate.
        self.eta = 0.05

        ###### special attributes ######

        self.length_val = length_val
        self.length_byte_len = length_byte_len
        # If the length should consider the length field itself.
        self.include_myself = include_myself
    
    ########## Get binary info ##########

    def get_binary_expression_inner(self):
        """Get binary expression."""
        return num2bytes(self.length_val, self.length_byte_len)

    ########## Update according to dependencies ##########
    
    def update_on_dependencies_inner(self):
        """
        Update the current BFN according to its dependencies.
        Calculate the sum of length of the dependency fields.
        """
        len_sum = self.length_byte_len if self.include_myself else 0
        for dependency in self.dependencies:
            len_sum = len_sum + dependency.get_binary_length()
        self.length_val = len_sum

    ########## Methods for generating random mutation ##########

    def random_length(self):
        """
        Return a random length fitting in `self.length_byte_len` bytes 
        """
        byte_seq = random.randbytes(self.length_byte_len)
        return bytes2num(byte_seq)

    ########## Methods for applying mutation ##########

    @BinaryFieldNode.set_function_decorator
    def set_length(self, length_val: int):
        """
        Set the length_val of current BFN.
        """
        self.length_val = length_val
    
    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set + [
        BinaryFieldNode.MutationItem(random_length, set_length)
    ]


class ASN_BFN(BinaryFieldNode):
    """
    The AS number field.
    """
    def __init__(self,
                 asn: int,
                 asn_byte_len=2):
        """Initialize the ASN BFN."""

        ###### Basic attributes ######

        self.children : dict[str,BinaryFieldNode] = {}
        self.parent : BinaryFieldNode = None
        self.dependencies = dict[str,BinaryFieldNode] = {}
        self.depend_on_me = dict[str,BinaryFieldNode] = {}
        self.detached = False
        self.binary_content : bytes = None
        self.prefix : bytes = b''
        self.suffix : bytes = b''

        # Initialize all weights to 1.
        # IMPORTANT: use the `mutation_set` of current class!
        self.weights = np.ones(len(ASN_BFN.mutation_set))
        # Normalize
        self.weights /= np.sum(self.weights)
        # Set the learning rate.
        self.eta = 0.05

        ###### special attributes ######

        self.asn = asn
        self.asn_byte_len = asn_byte_len
    
    ########## Get binary info ##########

    def get_binary_expression_inner(self):
        """Get binary expression."""
        return num2bytes(self.asn, self.asn_byte_len)

    ########## Update according to dependencies ##########
    
    def update_on_dependencies_inner(self):
        """
        Update the current BFN according to its dependencies.
        This BFN do not have dependencies.
        """
        # You should not raise error because of `attach` function
        return

    ########## Methods for generating random mutation ##########

    def random_asn(self):
        """
        Return a random AS number.
        Only care about the number, may not be legal.
        """
        byte_seq = random.randbytes(self.asn_byte_len)
        return bytes2num(byte_seq)

    def random_legal_asn(self):
        """
        Return a random AS number.
        The AS numbr is guaranteed to be legal.
        """
        if self.asn_byte_len == 2:
            return random.randint(1,64495)
        elif self.asn_byte_len == 4:
            return random.randint(65536, 4199999999)
        else:
            # You are using an illegal AS number length
            # Do not care whether the result is legal now.
            byte_seq = random.randbytes(self.asn_byte_len)
            return bytes2num(byte_seq)
    
    # To be checked. 
    def random_short_asn(self):
        """
        Random short AS number.
        Normally a short asn should not be used in long ASN expression.
        """
        return random.randint(1,64495)

    ########## Methods for applying mutation ##########

    @BinaryFieldNode.set_function_decorator
    def set_asn(self, asn: int):
        """
        Set the ASN of current BFN.
        """
        self.asn = asn

    ########## Method for selecting mutation ##########

    # Overwrite the father class' mutation_set
    mutation_set = BinaryFieldNode.mutation_set + [
        BinaryFieldNode.MutationItem(random_asn, set_asn),
        BinaryFieldNode.MutationItem(random_legal_asn, set_asn),
        BinaryFieldNode.MutationItem(random_short_asn, set_asn)
    ]


