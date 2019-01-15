# Import standard python libraries
import sys, os

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import sensor
from device.utilities import bitwise


def test_get_bit_from_byte():
    byte = 0x4C
    bit = bitwise.get_bit_from_byte(7, byte)
    assert bit == 0
    bit = bitwise.get_bit_from_byte(6, byte)
    assert bit == 1
    bit = bitwise.get_bit_from_byte(5, byte)
    assert bit == 0
    bit = bitwise.get_bit_from_byte(4, byte)
    assert bit == 0
    bit = bitwise.get_bit_from_byte(3, byte)
    assert bit == 1
    bit = bitwise.get_bit_from_byte(2, byte)
    assert bit == 1
    bit = bitwise.get_bit_from_byte(1, byte)
    assert bit == 0
    bit = bitwise.get_bit_from_byte(0, byte)
    assert bit == 0


def test_get_byte_from_bit():
    bits = {7: 0, 6: 1, 5: 0, 4: 0, 3: 1, 2: 1, 1: 0, 0: 0}
    byte = bitwise.get_byte_from_bits(bits)
    assert byte == 0x4C
