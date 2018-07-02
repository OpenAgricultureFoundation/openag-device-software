# Import standard python libraries
import pytest, logging
from unittest import TestCase

# Import i2c elements
from device.comms.i2c2.main import I2C
from device.comms.i2c2.exceptions import ReadError, WriteError
from device.comms.i2c2.mux_simulator import MuxSimulator
from device.comms.i2c2.peripheral_simulator import PeripheralSimulator

# Enable logging output
logging.basicConfig(level=logging.DEBUG)


def test_init():
    i2c = I2C("Test", 2, 0x40, 0x77, 4, MuxSimulator(), PeripheralSimulator)


def test_read_empty():
    i2c = I2C("Test", 2, 0x40, 0x77, 4, MuxSimulator(), PeripheralSimulator)
    bytes_ = i2c.read(2)
    assert bytes_[0] == 0x00
    assert bytes_[1] == 0x00


def test_write_unknown():
    i2c = I2C("Test", 2, 0x40, 0x77, 4, MuxSimulator(), PeripheralSimulator)
    with pytest.raises(WriteError):
        i2c.write([0x01])


def test_write_read():
    class CustomPeripheralSimulator(PeripheralSimulator):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.writes = {bytes([0x01]): bytes([0x02])}

    i2c = I2C("Test", 2, 0x40, 0x77, 4, MuxSimulator(), CustomPeripheralSimulator)
    i2c.write([0x01])
    bytes_ = i2c.read(1)
    assert bytes_[0] == 0x02


def test_write_register():
    i2c = I2C("Test", 2, 0x40, 0x77, 4, MuxSimulator(), PeripheralSimulator)
    i2c.write_register(0x01, 0x02)


def test_read_empty_register():
    i2c = I2C("Test", 2, 0x40, 0x77, 4, MuxSimulator(), PeripheralSimulator)
    with pytest.raises(ReadError):
        byte = i2c.read_register(0x01)


def test_write_read_register():
    i2c = I2C("Test", 2, 0x40, 0x77, 4, MuxSimulator(), PeripheralSimulator)
    i2c.write_register(0x01, 0x02)
    byte = i2c.read_register(0x01)
    assert byte == 0x02


def test_read_custom_register():
    class CustomPeripheralSimulator(PeripheralSimulator):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.registers = {0xE7: 0x00}

    i2c = I2C("Test", 2, 0x40, 0x77, 4, MuxSimulator(), CustomPeripheralSimulator)
    assert i2c.read_register(0xE7) == 0x00
