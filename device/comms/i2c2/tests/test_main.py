# Import standard python libraries
import pytest

# Import i2c elements
from device.comms.i2c2.main import I2C
from device.comms.i2c2.simulator import Simulator
from device.comms.i2c2.exceptions import InitializationError, ReadError


def test_init():
	i2c = I2C("Test", 2, 0x40, Simulator=Simulator)


def test_write():
	i2c = I2C("Test", 2, 0x77, Simulator=Simulator)
	i2c.write([0x01])


def test_read_empty():
	i2c = I2C("Test", 2, 0x77, Simulator=Simulator)
	bytes_ = i2c.read(1)
	assert bytes_[0] == 0x00


def test_write_read():
	i2c = I2C("Test", 2, 0x77, Simulator=Simulator)
	i2c.write([0x01])
	bytes_ = i2c.read(1)
	assert bytes_[0] == 0x01


def test_write_register():
	i2c = I2C("Test", 2, 0x77, Simulator=Simulator)
	i2c.write_register(0x01, 0x02)


def test_read_empty_register():
	i2c = I2C("Test", 2, 0x77, Simulator=Simulator)
	with pytest.raises(ReadError):
		byte = i2c.read_register(0x01)


def test_write_read_register():
	i2c = I2C("Test", 2, 0x77, Simulator=Simulator)
	i2c.write_register(0x01, 0x02)
	byte = i2c.read_register(0x01)
	assert byte == 0x02
