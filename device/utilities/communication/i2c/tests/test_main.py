# Import standard python libraries
import pytest, logging, threading
from unittest import TestCase

# Import utilities
from device.utilities.bitwise import byte_str

# Import i2c elements
from device.utilities.communication.i2c.main import I2C
from device.utilities.communication.i2c.exceptions import ReadError, WriteError
from device.utilities.communication.i2c.mux_simulator import MuxSimulator
from device.utilities.communication.i2c.peripheral_simulator import PeripheralSimulator

# Enable logging output
logging.basicConfig(level=logging.DEBUG)


def test_init():
    i2c = I2C(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x40,
        mux=0x77,
        channel=4,
        mux_simulator=MuxSimulator(),
        PeripheralSimulator=PeripheralSimulator,
    )


def test_read_empty():
    i2c = I2C(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x40,
        mux=0x77,
        channel=4,
        mux_simulator=MuxSimulator(),
        PeripheralSimulator=PeripheralSimulator,
    )
    bytes_ = i2c.read(2)
    assert bytes_[0] == 0x00
    assert bytes_[1] == 0x00


def test_write_unknown():
    i2c = I2C(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x40,
        mux=0x77,
        channel=4,
        mux_simulator=MuxSimulator(),
        PeripheralSimulator=PeripheralSimulator,
    )
    with pytest.raises(WriteError):
        i2c.write([0x01])


def test_write_read():
    class CustomPeripheralSimulator(PeripheralSimulator):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.writes = {byte_str(bytes([0x01])): bytes([0x02])}

    i2c = I2C(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x40,
        mux=0x77,
        channel=4,
        mux_simulator=MuxSimulator(),
        PeripheralSimulator=CustomPeripheralSimulator,
    )
    i2c.write(bytes([0x01]))
    bytes_ = i2c.read(1)
    assert bytes_[0] == 0x02


def test_write_register():
    i2c = I2C(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x40,
        mux=0x77,
        channel=4,
        mux_simulator=MuxSimulator(),
        PeripheralSimulator=PeripheralSimulator,
    )
    i2c.write_register(0x01, 0x02)


def test_read_empty_register():
    i2c = I2C(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x40,
        mux=0x77,
        channel=4,
        mux_simulator=MuxSimulator(),
        PeripheralSimulator=PeripheralSimulator,
    )
    with pytest.raises(ReadError):
        byte = i2c.read_register(0x01)


def test_write_read_register():
    i2c = I2C(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x40,
        mux=0x77,
        channel=4,
        mux_simulator=MuxSimulator(),
        PeripheralSimulator=PeripheralSimulator,
    )
    i2c.write_register(0x01, 0x02)
    byte = i2c.read_register(0x01)
    assert byte == 0x02


def test_read_custom_register():
    class CustomPeripheralSimulator(PeripheralSimulator):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.registers = {0xE7: 0x00}

    i2c = I2C(
        name="Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x40,
        mux=0x77,
        channel=4,
        mux_simulator=MuxSimulator(),
        PeripheralSimulator=CustomPeripheralSimulator,
    )
    assert i2c.read_register(0xE7) == 0x00
