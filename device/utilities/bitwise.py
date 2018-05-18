""" Bitwise utility functions. """


def get_bit_from_byte(bit, byte):
    """ Gets a bit from a byte. """
    
    # Check bit value 0-7
    if bit not in range(0, 8):
    	raise ValueError("Invalid bit value, must be in range 0-7")

    # Get bit value
    mask = 0x1 << bit
    return (byte & mask) >> bit
