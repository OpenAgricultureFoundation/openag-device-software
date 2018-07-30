from typing import Tuple

RH = 48.5
T = 23.5


def convert_base_1_512(n: float) -> Tuple[int, int]:
    """Convert a float into base 1/512 msb and lsb."""

    # Initialize byte list
    byte_list = []

    # Iterage over 16 bits starting with most significant
    for i in range(15, -1, -1):

        # Get float value from bit in base 1/512 byte
        val = 1.0 / 512 * 2 ** i

        # Check if bit at position i should be enabled
        if n >= val:
            byte_list.append(1)

            # If bit enabled, subtract float value from number
            n = n - val

        # Check if bit at position i should be disabled
        else:
            byte_list.append(0)

    # Convert byte list to msb and lsb
    msb_list = byte_list[:8]
    lsb_list = byte_list[8:]

    return msb_list, lsb_list


print(convert_base_1_512(T))


# def conver(n, b):
#     a = 0
#     i = 0
#     while n:
#         n, r = divmod(n, b)
#         a += 10 ** i * r
#         i += 1

#     return a


# print(conver(16, 8))
