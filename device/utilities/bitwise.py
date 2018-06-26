""" Bitwise utility functions. """

def get_bit_from_byte(bit, byte):
    """ Gets a bit from a byte. """
    
    # Check bit value 0-7
    if bit not in range(0, 8):
    	raise ValueError("Invalid bit value, must be in range 0-7")

    # Get bit value
    mask = 0x1 << bit
    return (byte & mask) >> bit


def get_byte_from_bits(bits) -> int:
	""" Gets a byte from an ordered dict of bits. """

	# Verify bits structure
	for position in range(8):
		if position not in bits:
			raise ValueError("Invalid bits, must contain entry for bit at position {}".format(position))

	# Get byte value
	byte = bits[0]
	for i in range(1, 8):
		byte += bits[i] << i

	# Return byte value
	return byte
