# Import standard python modules
import fcntl, io
from typing import Optional, Type, Callable, cast, Any, TypeVar
from types import TracebackType

# Import device utilities
from device.utilities.logger import Logger

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
    """Manages byte-level device IO.

    Attributes:
        name -- name of device
        bus -- device i2c bus
    """

    def __init__(self, name: str, bus: int) -> None:

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
            device_name = "/dev/i2c-{}".format(self.bus)
            self.io = io.open(device_name, "r+b", buffering=0)
        except PermissionError as e:
            message = "Unable to open device io: {}".format(device_name)
            raise InitError(message, logger=self.logger) from e

    def close(self) -> None:
        """Closes io stream."""
        try:
            self.io.close()
        except:
            self.logger.exception("Unable to close")

    @manage_io
    def write(self, address: int, bytes_: bytes) -> None:
        """ Writes bytes to IO stream. """
        try:
            fcntl.ioctl(self.io, I2C_SLAVE, address)
            self.io.write(bytes_)
        except IOError as e:
            message = "Unable to write: {}".format(bytes_)
            raise WriteError(message) from e

    @manage_io
    def read(self, address: int, num_bytes: int) -> bytes:
        """Reads bytes from io stream."""
        try:
            fcntl.ioctl(self.io, I2C_SLAVE, address)
            return bytes(self.io.read(num_bytes))
        except IOError as e:
            message = "Unable to read {} bytes".format(num_bytes)
            raise ReadError(message) from e

    @manage_io
    def read_register(self, address: int, register: int) -> int:
        """Reads register from io stream."""
        try:
            reg = c_uint8(register)
            result = c_uint8()
            request = make_i2c_rdwr_data(  # type: ignore
                [
                    (address, 0, 1, pointer(reg)),  # write cmd register
                    (address, I2C_M_RD, 1, pointer(result)),  # read 1 byte as result
                ]
            )
            fcntl.ioctl(self.io.fileno(), I2C_RDWR, request)
            byte_ = int(result.value)
            message = "Read register 0x{:02X}, value: 0x{:02X}".format(register, byte_)
            self.logger.debug(message)
            return byte_
        except IOError as e:
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
        self.write(address, bytes([register, value]))
