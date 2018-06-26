# Import standard python libraries
import sys

# Import driver module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.comms.i2c import I2C
except:
    # ... if running tests from same dir as i2c_driver.py
    sys.path.append("../../")
    from device.comms.i2c import I2C


def test_init():
    i2c = I2C("Test", 2, 0x77, simulate=True)


def test_write():
    i2c = I2C("Test", 2, 0x77, simulate=True)
    error = i2c.write([0x01])
    assert error.exists() == False


def test_write_raw():
    i2c = I2C("Test", 2, 0x77, simulate=True)
    error = i2c.write_raw(0x01)
    assert error.exists() == False


def test_read():
    i2c = I2C("Test", 2, 0x77, simulate=True)
    byte_array, error = i2c.read(1)
    assert error.exists() == False
    assert type(byte_array) == bytearray
    assert len(byte_array) == 1


def test_read_raw():
    i2c = I2C("Test", 2, 0x77, simulate=True)
    bytes_, error = i2c.read_raw(1)
    assert error.exists() == False
    assert type(bytes_) == bytes
    assert len(bytes_) == 1


def test_read_register():
    i2c = I2C("Test", 2, 0x77, simulate=True)
    byte, error = i2c.read_register(0x77)
    assert error.exists() == False
    assert type(byte) == int
