# Import standard python libraries
import os, sys

# Get current working directory
cwd = os.getcwd()
print("Running from: {}".format(cwd))

# Set correct import path
if cwd.endswith("comms"):
    print("Running locally")
    sys.path.append("../../../../")
elif cwd.endswith("openag-device-software"):
    print("Running globally")
else:
    print("Running from invalid location")
    sys.exit(0)

# Import i2c
from device.comms.i2c_exc import I2C


def test_init():
	i2c = I2C("Test", 2, 0x77, simulate=True)


def test_write():
	i2c = I2C("Test", 2, 0x77, simulate=True)
	i2c.write([0x01])


def test_write_raw():
	i2c = I2C("Test", 2, 0x77, simulate=True)
	i2c.write_raw(0x01)


def test_read():
	i2c = I2C("Test", 2, 0x77, simulate=True)
	byte_array = i2c.read(1)
	assert len(byte_array) == 1


def test_read_raw():
	i2c = I2C("Test", 2, 0x77, simulate=True)
	bytes_ = i2c.read_raw(1)
	assert type(bytes_) == bytes
	assert len(bytes_) == 1


def test_read_register():
	i2c = I2C("Test", 2, 0x77, simulate=True)
	byte = i2c.read_register(0x77)
	assert byte == 0x00
