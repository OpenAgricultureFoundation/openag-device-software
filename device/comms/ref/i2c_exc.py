# Import standard python libraries
import fcntl, io, time, logging, threading, struct
from typing import Optional, List
from ctypes import *

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.functools import retry


class I2C(object):
    """I2C communication device. Can communicate with device directly or 
    via an I2C mux.

    Attributes:
        name -- name of device
        bus --  device bus
        address -- device address
        mux -- device mux address
        channel -- device mux channel
        simulate -- sets simulation mode
    """

    # Initialize I2C communication options
    I2C_SLAVE = 0x0703  # Use this slave address
    I2C_RDWR = 0x0707  # Combined R/W transfer (one STOP only)
    I2C_M_RD = 0x0001  # read data, from slave to master

    def __init__(
        self,
        name: str,
        bus: int,
        address: int,
        mux: Optional[int] = None,
        channel: Optional[int] = None,
        simulate: bool = False,
    ) -> None:

        # Initialize passed in parameters
        self.name = name
        self.bus = bus
        self.address = address
        self.mux = mux
        self.channel = channel
        self.simulate = simulate

        # Initialize logger instance
        logger_name = "I2C({})".format(self.name)
        self.logger = Logger(name=logger_name, dunder_name=__name__)

        # Check if simulated
        if self.simulate:
            self.logger.debug("Simulated initialization")
            return

        # I2C not simulated, open device
        try:
            device_name = "/dev/i2c-{}".format(bus)
            self.device = io.open(device_name, "r+b", buffering=0)
        except PermissionError as e:
            raise InitializationError(
                "Unable to open device: {}".format(device_name)
            ) from e

        # Verify device exists by trying to read from device
        try:
            byte = self.read(1)
        except ReadError as e:
            raise InitializationError("Unable to detect device") from e
        except MuxError as e:
            raise InitializationError("Unable to set mux") from e

        # Initialization successful!
        self.logger.debug("Successfully initialized")

    def __del__(self):
        """Clean up any resources used by the I2c instance."""
        self.close()

    def __enter__(self):
        """Context manager enter function."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit function, ensures resources are cleaned up."""
        self.close()
        return False  # Don't suppress exceptions.

    @retry(WriteError, tries=5, delay=0.1, backoff=2)
    def write(self, byte_list: List[int], retry: bool = False):
        """Writes byte list to device. Converts byte list to byte array then 
        sends bytes. Returns error message. """

        # Handle mux interactions
        self.set_mux(retry=retry)

        # Build byte array and string
        byte_array = bytearray(byte_list)
        byte_string = "".join("0x{:02X} ".format(b) for b in byte_array)

        # Check if i2c is simulated
        if self.simulate:
            self.logger.debug("Simulating writing: {}".format(byte_string))
            return

        # I2C is not simulated!
        self.logger.debug("Writing: {}".format(byte_string))

        # Write to i2c device
        try:
            with threading.Lock():
                fcntl.ioctl(self.device, self.I2C_SLAVE, self.address)
                self.device.write(byte_array)
        except IOError as e:
            raise WriteError("Unable to write to i2c device", byte_list) from e

    @retry(WriteError, tries=5, delay=0.1, backoff=2)
    def write_raw(self, bytes_: bytearray, retry: bool = False) -> None:
        """ Writes raw bytes to device. """

        # Set mux if enabled
        self.set_mux(retry=retry)

        # Check if i2c is simulated
        if self.simulate:
            self.logger.debug("Simulating writing: {}".format(bytes_))
            return

        # I2c is not simulated!
        self.logger.debug("Writing: {}".format(bytes_))

        # Write raw to i2c device
        try:
            with threading.Lock():
                fcntl.ioctl(self.device, self.I2C_SLAVE, self.address)
                self.device.write(bytes_)
        except IOError as e:
            message = "Unable to write raw bytes: {}".format(bytes_)
            raise WriteError(message) from e

    @retry(ReadError, tries=5, delay=0.1, backoff=2)
    def read(self, num_bytes: int, retry: bool = False) -> bytearray:
        """ Reads num bytes from device. Returns byte array. """
        self.logger.debug("Reading {} bytes".format(num_bytes))

        # Handle mux interactions
        self.set_mux(retry=retry)

        # Check if i2c is simulated
        if self.simulate:
            byte_array = bytearray(num_bytes)
            byte_string = "".join("0x{:02X} ".format(b) for b in byte_array)
            self.logger.debug("Simulated read: {}".format(byte_string))
            return byte_array

        # I2c is not simulated!
        try:
            with threading.Lock():
                fcntl.ioctl(self.device, self.I2C_SLAVE, self.address)
                raw_bytes = self.device.read(num_bytes)
                byte_array = bytearray(raw_bytes)
                byte_string = "".join("0x{:02X} ".format(b) for b in byte_array)
            self.logger.debug("Read: {}".format(byte_string))
            return byte_array
        except IOError as e:
            message = "Unable to read {} bytes".format(num_bytes)
            raise ReadError(message) from e

    @retry(ReadError, tries=5, delay=0.1, backoff=2)
    def read_raw(self, num_bytes: int, retry: bool = False) -> bytes:
        """Reads num bytes from device. Returns raw bytes."""

        # Set mux if enabled
        self.set_mux(retry=retry)

        # Check if i2c is simulated
        if self.simulate:
            bytes_ = bytes(num_bytes)
            self.logger.debug("Simulated read raw: {}".format(bytes_))
            return bytes_

        # I2c is not simulated!
        try:
            with threading.Lock():
                bytes_ = self.device.read(num_bytes)
            self.logger.debug("Read raw: {}".format(bytes_))
            return bytes_
        except IOError as e:
            message = "Unable to read {} raw bytes".format(num_bytes)
            raise ReadError(message)

    @retry(ReadError, tries=5, delay=0.1, backoff=2)
    def read_register(self, address: int, retry: bool = False) -> int:
        """ Reads byte stored in register at address. """

        # Set mux if enabled
        self.set_mux(retry=retry)

        # Check if i2c is simulated
        if self.simulate:
            byte_ = bytes(1)[0]
            self.logger.debug("Simulated read register: {}".format(byte_))
            return byte_

        # I2c is not simulated!
        try:
            with threading.Lock():
                reg = c_uint8(address)
                result = c_uint8()
                request = make_i2c_rdwr_data(
                    [
                        (self.address, 0, 1, pointer(reg)),  # write cmd register
                        (
                            self.address, self.I2C_M_RD, 1, pointer(result)
                        ),  # read 1 byte as result
                    ]
                )
                fcntl.ioctl(self.device.fileno(), self.I2C_RDWR, request)
                byte_ = result.value
            self.logger.debug("Read register: {}".format(byte_))
            return byte_
        except IOError as e:
            message = "Unable to read register 0x{:02}".format(address)
            raise ReadError(message) from e

    @retry(MuxError, tries=5, delay=0.1, backoff=2)
    def set_mux(self, retry: bool = False):
        """ Sets mux to channel if enabled. """

        # Check if mux is used
        if self.mux == None:
            return

        # Mux is used!
        if self.channel == None:
            raise MuxError(
                "Channel cannot be None if using mux", self.mux, self.channel
            )

        # Build byte array and string
        channel_byte = 0x01 << self.channel
        byte_list = [channel_byte]
        byte_array = bytearray(byte_list)
        byte_string = "".join("0x{:02X} ".format(b) for b in byte_array)

        # Check if mux is simulated
        if self.simulate:
            self.logger.debug(
                "Simulating setting mux 0x{:02X} to channel {}, writing: 0x{:02X}".format(
                    self.mux, self.channel, channel_byte
                )
            )
            return

        # Mux is not simulated, set mux to channel
        try:
            with threading.Lock():
                self.logger.debug(
                    "Setting mux 0x{:02X} to channel {}, writing: 0x{:02X}".format(
                        self.mux, self.channel, channel_byte
                    )
                )
                fcntl.ioctl(self.device, self.I2C_SLAVE, self.mux)
                self.device.write(byte_array)
        except IOError as e:
            raise MuxError("Unable to write to mux", self.mux, self.channel) from e

    def close(self):
        """ Closes device. """
        if not self.simulate:
            self.device.close()


def scan(address_range=None, mux_range=None, channel_range=None):
    """Scan for devices at specified address, mux, and channel ranges."""
    ...
