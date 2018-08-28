from typing import Tuple

import sys

sys.path.append("../../../../")
from device.utilities.bitwise import get_byte_from_bit_list

RH = 48.5
T = 23.5


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


msb, lsb = convert_base_1_512(50)
print("[0x{:02X}, 0x{:02X}]".format(msb, lsb))
