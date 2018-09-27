""" Bitwise utility functions. """
from typing import List, Tuple, Dict


def get_bit_from_byte(bit: int, byte: int) -> int:
    """ Gets a bit from a byte. """

    # Check bit value 0-7
    if bit not in range(0, 8):
        raise ValueError("Invalid bit value, must be in range 0-7")

    # Get bit value
    mask = 0x1 << bit
    return (byte & mask) >> bit


def get_byte_from_bits(bits: Dict) -> int:
    """ Gets a byte from an ordered dict of bits. """

    # Verify bits structure
    for position in range(8):
        if position not in bits:
            message = "Invalid bits, must contain entry for bit at position {}".format(
                position
            )
            raise ValueError(message)

    # Get byte value
    byte = bits[0]
    for i in range(1, 8):
        byte += bits[i] << i

        # Return byte value
    return int(byte)


def get_byte_from_bit_list(bits: List[int]) -> int:
    """ Gets a byte from a list of bits. """

    # Verify bits structure
    if len(bits) != 8:
        raise ValueError("Invalid bit list, must contain 8 bits")

    # Get byte value
    byte = bits[0]
    for i in range(1, 8):

        # Check valid bit value
        if bits[i] != 0 and bits[i] != 1:
            raise ValueError("Invalid bit[{}]={}, must be 1 or 0".format(i, bits[i]))

        # Add value to byte
        byte += bits[i] << i

        # Return byte value
    return byte


def byte_str(bytes_: bytes) -> str:
    """Returns bytes in string representation."""
    string = "[" + "".join("0x{:02X}, ".format(b) for b in bytes_)
    if string == "[":
        return string + "]"
    else:
        return string[:-2] + "]"


def convert_base_1_512(n: float) -> Tuple[int, int]:
    """Convert a float into base 1/512 msb and lsb."""

    # Initialize bit list
    bits = []

    # Iterage over 16 bits starting with most significant
    for i in range(15, -1, -1):

        # Get float value from bit in base 1/512 byte
        val = 1.0 / 512 * 2 ** i

        # Check if bit at position i should be enabled
        if n >= val:
            bits.append(1)

            # If bit enabled, subtract float value from number
            n = n - val

        # Check if bit at position i should be disabled
        else:
            bits.append(0)

    # Adjust endianness
    msb_bits = list(reversed(bits[:8]))
    lsb_bits = list(reversed(bits[8:]))

    # Convert byte list to msb and lsb
    msb = get_byte_from_bit_list(msb_bits)
    lsb = get_byte_from_bit_list(lsb_bits)

    return msb, lsb
