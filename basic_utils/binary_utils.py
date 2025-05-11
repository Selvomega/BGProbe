"""
Functions used for binary processing.
"""

import socket

def num2bytes(num, octet_num, overflow_escape=False) -> bytes:
    """
    Convert the number into the binary expression with 1 octet
    `octet_num` should usually be 1 or 2.
    """
    bit_num = 8*octet_num
    if not 0 <= num < 2**bit_num:
        if not overflow_escape:
            print(f"Warning: The number {num} is not in the range 0-{2**bit_num-1}")
            # raise ValueError(f"The number {num} is not in the range 0-{2**bit_num-1}")
        num = num % (2**bit_num)  # Wrap around if out of range
    return num.to_bytes(octet_num, byteorder="big")

# # This part is annotated because there is a different definition with the same name in `basic_types.py`.
# def ip2bytes(ip) -> bytes:
#     """
#     Converts an IPv4 address from its dotted-decimal string format into a 4-byte binary representation.
#     """
#     return socket.inet_aton(ip)

def substitute(original, new_field, begin_byte_num) -> bytes:
    """
    Replace part of the original bytes with the substitute bytes starting at `begin_byte_num`.
    """
    if not 0 <= begin_byte_num <= len(original):
        raise ValueError(f"The length of {begin_byte_num} ({len(begin_byte_num)}) is out of range")

    return original[:begin_byte_num] + new_field + original[begin_byte_num + len(new_field):]

def bstr2bytes(bstr):
    """
    Convert a binary string into bytes
    """
    if len(bstr) % 8 != 0:
        raise ValueError("Binary string length must be a multiple of 8")
    if not is_binary_string(bstr):
        raise ValueError(f"The string must contain only 0 and 1 (your string: {bstr})")
    print(int(bstr[:8], 2))
    return b''.join(int(bstr[i:i+8], 2).to_bytes(1, byteorder="big") for i in range(0, len(bstr), 8))

def bytes2bstr(b:bytes):
    """
    Convert bytes into a binary string
    """
    return ''.join(f'{byte:08b}' for byte in b)

def bytes2num(b: bytes) -> int:
    """
    Convert bytes into a number.
    """
    return int.from_bytes(b, byteorder='big')

def is_binary_string(s):
    """
    Check if a python string contains only `0` and `1`.
    """
    return set(s).issubset({'0', '1'})

def list2byte(bits_list) -> bytes:
    """
    Convert a zero-one list with length 8 to the corresponding byte.
    Example:
        >>> list_to_byte([1, 0, 1, 0, 1, 0, 1, 0])
        b'\xaa'
    """
    if len(bits_list) != 8:
        raise ValueError("The length of the input list must be 8")
    
    # Check if the list elements are all 0 or 1.
    if any(bit not in (0, 1) for bit in bits_list):
        raise ValueError("The list element must be 0 or 1!")
    
    # Compose the binary bits to an integer.
    byte_value = 0
    for bit in bits_list:
        byte_value = (byte_value << 1) | bit
    
    # Conver the integer to a byte
    return bytes([byte_value])

def make_bytes_displayable(byte_seq: bytes) -> str:
    """
    Convert the bytes to a displayable version.
    """
    return '\\x' + '\\x'.join(f'{b:02x}' for b in byte_seq)

def mrt_to_binary(file_path) -> bytes:
    """
    Read the MRT file into a byte sequence.
    """
    with open(file_path, 'rb') as file:
        file_bytes = file.read()
    return file_bytes
