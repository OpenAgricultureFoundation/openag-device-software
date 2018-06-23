# Import standard python modules
import fcntl, io
from typing import Optional, Type
from types import TracebackType

# Import device utilities
from device.utilities.logger import Logger

# Import i2c package elements
from device.comms.i2c2.exceptions import InitializationError
from device.comms.i2c2.exceptions import InitializationError, WriteError, ReadError, MuxError
from device.comms.i2c2.utilities import I2CConfig

# Initialize I2C communication options
I2C_SLAVE = 0x0703 # Use this slave address
I2C_RDWR = 0x0707  # Combined R/W transfer (one STOP only)
I2C_M_RD = 0x0001  # read data, from slave to master


class DeviceIO:
    """Manages byte-level device IO.

    Attributes:
        name -- name of device
        bus -- device i2c bus
    """

    def __init__(self, config: I2CConfig) -> None:

        # Initialize logger
        logger_name = "DeviceIO({})".format(config.name)
        self.logger = Logger(
            name = config.name,
            dunder_name = __name__,
        )

        # Open IO stream
        try:
            device_name = "/dev/i2c-{}".format(config.bus)
            self.io = io.open(device_name, "r+b", buffering=0)
        except PermissionError as e:
            self.io = None
            message = "Unable to open device io: {}".format(device_name)
            raise InitializationError(message, logger=self.logger) from e


    def __del__(self) -> None:
        """Clean up any resources used by the I2c instance."""
        self.close()


    def __enter__(self) -> object:
        """Context manager enter function."""
        return self


    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], 
        exc_tb: Optional[TracebackType]) -> bool:
        """Context manager exit function, ensures resources are cleaned up."""
        self.close()
        return False  # Don't suppress exceptions

    def close(self):
        """Closes io."""
        if self.io != None:
            self.io.close()


    def write(self, address: int, bytes_: bytes) -> None:
        """ Writes bytes to IO stream. """
        try:
            with threading.Lock():
                fcntl.ioctl(self.io, I2C_SLAVE, address)
                self.io.write(bytes_)
        except IOError as e:
            message = "Unable to write: {}".format(bytes_)
            raise WriteError(message) from e


    def read(self, address: int, num_bytes: int) -> bytes:
        """Reads bytes from io stream."""
        try:
            with threading.Lock():
                fcntl.ioctl(self.io, I2C_SLAVE, address)
                return self.io.read(num_bytes)
        except IOError as e:
            message = "Unable to read {} bytes".format(num_bytes)
            raise ReadError(message) from e


    def read_register(self, address: int, register: int) -> int:
        """Reads register from io stream."""
        try:
            with threading.Lock():
                reg = c_uint8(register)
                result = c_uint8()
                request = make_i2c_rdwr_data([
                    (address, 0, 1, pointer(reg)), # write cmd register
                    (address, I2C_M_RD, 1, pointer(result)) # read 1 byte as result
                ])
                fcntl.ioctl(self.device.fileno(), self.I2C_RDWR, request)
                byte_ = result.value
            self.logger.debug("Register 0x{:02X}: 0x{:02X}".format(register, byte_))
            return byte_
        except IOError as e:
            message = "Unable to read register 0x{:02}".format(register)
            raise ReadError(message) from e


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
        self.write(address, bytes[register, value])
