# Import standard python libraries
import pytest, logging
from unittest import TestCase

# Import i2c elements
from device.comms.i2c2.main import I2C
from device.comms.i2c2.exceptions import ReadError
from device.comms.i2c2.utilities import I2CConfig
from device.comms.i2c2.mux_simulator import MuxSimulator
from device.comms.i2c2.peripheral_simulator import PeripheralSimulator

# Enable logging output
logging.basicConfig(level=logging.DEBUG)


def test_init():
    i2c = I2C("Test", 2, 0x40, 0x77, 4, MuxSimulator(), PeripheralSimulator)


# def test_write():
#     config = I2CConfig("Test", 2, 0x40, 0x77, 4, MuxSimulator())
#     i2c = I2C(config, PeripheralSimulator)
#     i2c.write([0x01])


# def test_read_empty():
#     config = I2CConfig("Test", 2, 0x40, 0x77, 4, MuxSimulator())
#     i2c = I2C(config, PeripheralSimulator)
#     bytes_ = i2c.read(1)
#     assert bytes_[0] == 0x00


# def test_write_read():
#     config = I2CConfig("Test", 2, 0x40, 0x77, 4, MuxSimulator())
#     i2c = I2C(config, PeripheralSimulator)
#     i2c.write([0x01])
#     bytes_ = i2c.read(1)
#     assert bytes_[0] == 0x01


# def test_write_register():
#     config = I2CConfig("Test", 2, 0x40, 0x77, 4, MuxSimulator())
#     i2c = I2C(config, PeripheralSimulator)
#     i2c.write_register(0x01, 0x02)


# def test_read_empty_register():
#     config = I2CConfig("Test", 2, 0x40, 0x77, 4, MuxSimulator())
#     i2c = I2C(config, PeripheralSimulator)
#     with pytest.raises(ReadError):
#         byte = i2c.read_register(0x01)


# def test_write_read_register():
#     config = I2CConfig("Test", 2, 0x40, 0x77, 4, MuxSimulator())
#     i2c = I2C(config, PeripheralSimulator)
#     i2c.write_register(0x01, 0x02)
#     byte = i2c.read_register(0x01)
#     assert byte == 0x02
