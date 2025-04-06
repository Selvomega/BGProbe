from enum import Enum
from binary_utils.utils import *

from .basic_types import BinaryField

class PathAttributeType(Enum):
    """
    BGP path attribute code
    """
    RESERVED = 0
    ORIGIN = 1
    AS_PATH = 2
    NEXT_HOP = 3
    MULTI_EXIT_DISC = 4
    LOCAL_PREF = 5
    ATOMIC_AGGREGATE = 6
    AGGREGATOR = 7
    COMMUNITIES = 8
    ORIGINATOR_ID = 9
    CLUSTER_LIST = 10

class BaseAttr(BinaryField):
    """
    Base class of all attribute.
    """
    def __init__(self):
        """
        Initialize the binary parts of the attribute.
        The attribute in subclasses could have two parts: content part and binary part.
        They are both set in the `__init__` method of the subclass. 
        While the bianry part can be modified randomly, 
        the content part should always be set to legal values. 
        One can use the `reset` method to set the value of the binary part back to what is indicated in the content part
        """
        self.attr_flag_b : bytes = None
        self.attr_type_b : bytes = None
        self.attr_len_b : bytes = None
        self.attr_value_b : bytes = None

    def reset(self):
        """
        Reset the attribute into the original status.
        """
        pass

    def set_attr_flag(self,**kwargs):
        """
        Set the AttrFlag
        Does not guarantee the consistency with AttrLen!
        Three ways of passing parameters:
        1. optional:bool, transitive:bool, partial:bool, ext_len:bool, padding:str
        2. self_defined:bytes
        3. attribute:PathAttribute, ext_len:bool
        """
        def __inner1__(optional:bool,
                       transitive:bool,
                       partial:bool,
                       ext_len:bool,
                       padding:str='0000'):
            """
            Inner method 1 of modifying AttrFlag
            """
            temp_l = [optional,transitive,partial,ext_len]
            temp_str = ''.join('1' if b else '0' for b in temp_l)
            temp_full_str = temp_str+padding
            print(temp_full_str)
            return bstr2bytes(temp_full_str)
        def __inner2__(self_defined:bytes):
            """
            Inner method 2 of modifying AttrFlag
            """
            assert len(self_defined)==1
            return self_defined
        def __inner3__(attribute:PathAttributeType, ext_len:bool):
            """
            Inner method 2 of initializing AttrFlag
            """
            match attribute:
                case PathAttributeType.RESERVED:
                    raise ValueError(f"Invalid path attribute: {PathAttributeType.RESERVED}")
                case PathAttributeType.ORIGIN | PathAttributeType.AS_PATH | PathAttributeType.NEXT_HOP | PathAttributeType.LOCAL_PREF | PathAttributeType.ATOMIC_AGGREGATE:
                    return __inner1__(optional=False,
                                      transitive=True,
                                      partial=False,
                                      ext_len=ext_len)
                case PathAttributeType.AGGREGATOR | PathAttributeType.COMMUNITIES:
                    return __inner1__(optional=True,
                                      transitive=True,
                                      partial=False,
                                      ext_len=ext_len)
                case PathAttributeType.MULTI_EXIT_DISC | PathAttributeType.ORIGINATOR_ID | PathAttributeType.CLUSTER_LIST:
                    return __inner1__(optional=True,
                                      transitive=False,
                                      partial=False,
                                      ext_len=ext_len)
                case _:
                    raise ValueError(f"Path attribute {attribute} undefined!")
        if 'optional' in kwargs:
            optional = kwargs['optional']
            transitive = kwargs['transitive']
            partial = kwargs['partial']
            ext_len = kwargs['ext_len']
            padding = '0000' if 'padding' not in kwargs else kwargs['padding']
            self.attr_flag_b = __inner1__(optional=optional,
                                          transitive=transitive,
                                          partial=partial,
                                          ext_len=ext_len,
                                          padding=padding)
        elif 'self_defined' in kwargs:
            self_defined = kwargs['self_defined']
            self.attr_flag_b = __inner2__(self_defined=self_defined)
        elif 'attribute' in kwargs:
            attribute = kwargs['attribute']
            ext_len = kwargs['ext_len']
            self.attr_flag_b = __inner3__(attribute=attribute,
                                          ext_len=ext_len)
        else:
            raise ValueError(f"Invalid input parameters: {kwargs}")

    def set_attr_type(self,**kwargs):
        """
        Set the AttrType
        Two ways of passing parameters:
        1. self_defined: bytes
        2. attribute: PathAttribute
        3. int_value: int
        """
        def __inner1__(self_defined:bytes):
            """
            Inner method 1 of initializing AttrType
            """
            assert len(self_defined)==1
            return self_defined
        def __inner2__(attribute:PathAttributeType):
            """
            Inner method 2 of initializing AttrType
            """
            return __inner1__(attribute.value)
        def __inner3__(int_value: int):
            """
            Inner method 3 of initializing AttrType
            """
            return num2bytes(int_value, 1)
        if 'self_defined' in kwargs:
            self_defined = kwargs['self_defined']
            self.attr_type_b = __inner1__(self_defined=self_defined)
        elif 'attribute' in kwargs:
            attribute = kwargs['attribute']
            self.attr_type_b = __inner2__(attribute=attribute)
        elif 'int_value' in kwargs:
            int_value = kwargs['int_value']
            self.attr_type_b = __inner3__(int_value=int_value)
        else:
            raise ValueError(f"Invalid input parameters: {kwargs}")

    # To Check: how will the extended-length be selected
    def set_attr_len(self,**kwargs):
        """
        Set the AttrLen
        Does not guarantee the consistency with AttrFlag!
        Two ways of passing parameters:
        1. len: int
        2. self_defined: bytes
        """
        def __inner1__(length:int):
            """
            Inner method 1 of modifying AttrFlag
            """
            attr_flag_s = bytes2bstr(self.attr_flag_b)
            byte_num = 2 if attr_flag_s[3]==1 else 1
            return num2bytes(length,byte_num)
        def __inner2__(self_defined: bytes):
            """
            Inner method 2 of modifying AttrFlag
            """
            assert len(self_defined)==1 or len(self_defined)==2
            return self_defined
        if 'length' in kwargs:
            length = kwargs['length']
            self.attr_len_b = __inner1__(length=length)
        elif 'self_defined' in kwargs:
            self_defined = kwargs['self_defined']
            self.attr_len_b = __inner2__(self_defined=self_defined)
        else:
            raise ValueError(f"Invalid input parameters: {kwargs}")

    def set_attr_value(self,self_defined:bytes):
        """
        Set the value field of the attribute. 
        Can be overridden by its subclasses.
        """
        self.attr_value_b = self_defined

    def append_attr_value(self,self_defined:bytes):
        """
        Append the self-defined string to the end of the value field.
        The message length is corrected automatically by `generate_len` method
        """
        self.attr_value_b = self.attr_value_b + self_defined
        self.generate_len()

    def generate_len(self):
        """
        Generate the length field of the attribute automatically.
        This should be called when you want length consistency after you modify other parts of the attribute.
        """
        attr_flag_s = bytes2bstr(self.attr_flag_b)
        length_byte_num = 2 if attr_flag_s[3]==1 else 1
        length = len(self.attr_value_b)
        self.attr_len_b = num2bytes(length,length_byte_num)
    
    def get_type(self):
        """
        Get the type of the the attribute.
        """
        pass

    def get_binary_expression(self) -> bytes:
        """
        Get the binary expression of the attribute. 
        """
        return self.attr_flag_b + self.attr_type_b + self.attr_len_b + self.attr_value_b

    def get_binary_length(self):
        """
        Get the length of the attribute.
        """
        return bytes2num(self.attr_len_b)
