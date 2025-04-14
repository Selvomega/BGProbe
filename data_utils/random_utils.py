import random

def zero_one_sample():
    """sample uniformly from {0,1}."""
    return random.randint(0,1)

def random_byte() -> bytes:
    """Sample a random byte."""
    return random.randbytes(1)

def random_byte_sequence(length: int) -> bytes:
    """Sample a random byte sequence with given length."""
    return random.randbytes(length)

bb = random_byte_sequence(0)
print(bb)