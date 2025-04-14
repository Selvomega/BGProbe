from .binary_field_node import BinaryFieldNode
from data_utils.binary_utils import num2bytes

class ASN_BFN(BinaryFieldNode):
    """
    The AS number field.
    """
    def __init__(self,
                 asn: int,
                 asn_byte_len=2):
        """
        Initialize the ASN BFN.
        """

        ###### Basic attributes ######

        self.children : dict[str,BinaryFieldNode] = {}
        self.parent : BinaryFieldNode = None
        self.dependencies = dict[str,BinaryFieldNode] = {}
        self.depend_on_me = dict[str,BinaryFieldNode] = {}
        self.detached = False
        self.binary_content : bytes = None
        self.prefix : bytes = b''
        self.suffix : bytes = b''

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
        pass

    ########## Methods for generating random mutation ##########

    def random_asn(self):
        a = BinaryFieldNode.BFNUpdateRule()

    ########## Methods for applying mutation ##########

    @BinaryFieldNode.set_function_decorator
    def set_asn(self, asn):
        """
        Set the ASN of current BFN.
        """
        self.asn = asn
