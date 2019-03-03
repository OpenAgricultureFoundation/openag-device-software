# Import standard python modules
import fcntl, io, os
from typing import Optional, Type, Callable, cast, Any, TypeVar
from types import TracebackType

# Import device utilities
from device.utilities.logger import Logger

# Import usb-i2c driver
from pyftdi.i2c import I2cController, I2cIOError, I2cNackError

# Import i2c package elements
from device.utilities.communication.i2c.exceptions import (
    InitError,
    WriteError,
    ReadError,
    MuxError,
)
from device.utilities.communication.i2c.utilities import (
    make_i2c_rdwr_data,
    c_uint8,
    pointer,
)

# Initialize I2C communication options
I2C_SLAVE = 0x0703  # Use this slave address
I2C_RDWR = 0x0707  # Combined R/W transfer (one STOP only)
I2C_M_RD = 0x0001  # read data, from slave to master

# Initialize type checking variables
F = TypeVar("F", bound=Callable[..., Any])
ET = TypeVar("ET", bound=Optional[Type[BaseException]])
EV = TypeVar("EV", bound=Optional[BaseException])
EB = TypeVar("EB", bound=Optional[TracebackType])


def manage_io(func: F) -> F:
    """Manages opening/closing io stream."""

    def wrapper(*args, **kwds):  # type: ignore
        self = args[0]
        self.open()
        resp = func(*args, **kwds)
        self.close()
        return resp

    return cast(F, wrapper)


class DeviceIO(object):
    """Manages byte-level device IO."""

    def __init__(self, name: str, bus: Optional[int] = None) -> None:

        # Initialize parameters
        self.name = name
        self.bus = bus

        # Initialize logger
        logname = "DeviceIO({})".format(name)
        self.logger = Logger(logname, __name__)

        # Verify io exists
        self.logger.debug("Verifying io stream exists")
        self.open()
        self.close()

    def __del__(self) -> None:
        """Clean up any resources used by the I2c instance."""
        self.close()

    def __enter__(self) -> object:
        """Context manager enter function."""
        return self

    def __exit__(self, exc_type: ET, exc_val: EV, exc_tb: EB) -> bool:
        """Context manager exit function, ensures resources are cleaned up."""
        self.close()
        return False  # Don't suppress exceptions

    def open(self) -> None:
        """Opens io stream."""
        try:
            if os.getenv("IS_I2C_ENABLED") == "true":
                device_name = "/dev/i2c-{}".format(self.bus)
                self.io = io.open(device_name, "r+b", buffering=0)
            elif os.getenv("IS_USB_I2C_ENABLED") == "true":
                self.io = I2cController()
                self.io.configure("ftdi://ftdi:232h/1")  # type: ignore
            else:
                message = "Platform does not support i2c communication"
                raise InitError(message)
        except (PermissionError, I2cIOError, I2cNackError) as e:
            message = "Unable to open device io: {}".format(device_name)
            raise InitError(message, logger=self.logger) from e

    def close(self) -> None:
        """Closes io stream."""
        try:
            if os.getenv("IS_I2C_ENABLED") == "true":
                self.io.close()
            elif os.getenv("IS_USB_I2C_ENABLED") == "true":
                self.io.terminate()  # type: ignore
            else:
                message = "Platform does not support i2c communication"
                raise InitError(message)
        except:
            self.logger.exception("Unable to close")

    @manage_io
    def write(self, address: int, bytes_: bytes) -> None:
        """ Writes bytes to IO stream. """
        try:
            if os.getenv("IS_I2C_ENABLED") == "true":
                fcntl.ioctl(self.io, I2C_SLAVE, address)
                self.io.write(bytes_)
            elif os.getenv("IS_USB_I2C_ENABLED") == "true":
                device = self.io.get_port(address)  # type: ignore
                device.write(bytes_)
            else:
                message = "Platform does not support i2c communication"
                raise WriteError(message)
        except (IOError, I2cIOError, I2cNackError) as e:
            message = "Unable to write: {}".format(bytes_)
            raise WriteError(message) from e

    @manage_io
    def read(self, address: int, num_bytes: int) -> bytes:
        """Reads bytes from io stream."""
        try:
            if os.getenv("IS_I2C_ENABLED") == "true":
                fcntl.ioctl(self.io, I2C_SLAVE, address)
                return bytes(self.io.read(num_bytes))
            elif os.getenv("IS_USB_I2C_ENABLED") == "true":
                device = self.io.get_port(address)  # type: ignore
                bytes_ = device.read(readlen=num_bytes)
                return bytes(bytes_)
            else:
                message = "Platform does not support i2c communication"
                raise ReadError(message)
        except (IOError, I2cIOError, I2cNackError) as e:
            message = "Unable to read {} bytes".format(num_bytes)
            raise ReadError(message) from e

    @manage_io
    def read_register(self, address: int, register: int) -> int:
        """Reads register from io stream."""
        try:
            if os.getenv("IS_I2C_ENABLED") == "true":
                reg = c_uint8(register)
                result = c_uint8()
                request = make_i2c_rdwr_data(  # type: ignore
                    [
                        (address, 0, 1, pointer(reg)),  # write cmd register
                        (
                            address,
                            I2C_M_RD,
                            1,
                            pointer(result),
                        ),  # read 1 byte as result
                    ]
                )
                fcntl.ioctl(self.io.fileno(), I2C_RDWR, request)
                byte_ = int(result.value)
                message = "Read register 0x{:02X}, value: 0x{:02X}".format(
                    register, byte_
                )
                self.logger.debug(message)
                return byte_
            elif os.getenv("IS_USB_I2C_ENABLED") == "true":
                device = self.io.get_port(address)  # type: ignore
                byte_raw = device.read_from(register, readlen=1)
                byte = int(byte_raw[0])
                return byte
            else:
                message = "Platform does not support i2c communication"
                raise ReadError(message)
        except (IOError, I2cIOError, I2cNackError) as e:
            message = "Unable to read register 0x{:02}".format(register)
            raise ReadError(message) from e

    @manage_io
    def write_register(self, address: int, register: int, value: int) -> None:
        """ Writes bytes to IO stream. """

        # Check register within range
        if register not in range(256):
            message = "Invalid register addrress: {}, must be 0-255".format(register)
            raise WriteError(message)

        # Check value within range
        if value not in range(256):
            message = "Invalid register value: {}, must be 0-255".format(value)
            raise WriteError(message)

        # Write to register
        try:
            if os.getenv("IS_I2C_ENABLED") == "true":
                self.write(address, bytes([register, value]))
            elif os.getenv("IS_USB_I2C_ENABLED") == "true":
                device = self.io.get_port(address)  # type: ignore
                device.write_to(register, [value])
            else:
                message = "Platform does not support i2c communication"
                raise WriteError(message)
        except (IOError, I2cIOError, I2cNackError) as e:
            message = "Unable to write register 0x{:02}".format(register)
            raise WriteError(message) from e
