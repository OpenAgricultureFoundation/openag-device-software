# Import standard python libraries
import fcntl, io, time, logging, threading, struct
from typing import Optional, List, Type, overload
from types import TracebackType
from ctypes import *

# Import package elements
from device.comms.i2c2.exceptions import InitializationError, WriteError, ReadError, MuxError
from device.comms.i2c2.utilities import make_i2c_rdwr_data
from device.comms.i2c2.simulator import Simulator

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.functiontools import retry


class I2C(object):
    """I2C communication device. Can communicate with device directly or 
    via an I2C mux.

    Attributes:
        name -- name of device
        bus --  device bus
        address -- device address
        mux -- device mux address
        channel -- device mux channel
        simulator -- device simulator
    """


    def __init__(self, name: str, bus: int, address: int, mux: Optional[int] = None, 
        channel: Optional[int] = None, Simulator: Optional[Simulator] = None) -> None:

        # Initialize passed in parameters
        self.name = name
        self.bus = bus
        self.address = address
        self.mux = mux
        self.channel = channel

        # Initialize logger instance
        logger_name = "I2C({})".format(self.name)
        self.logger = Logger(
            name = logger_name,
            dunder_name = __name__,
        )

        if Simulator != None:
            self.Device = Simulator
        else:
            self.Device = Device

        with device as self.Device(bus=2):
            byte = device.read_register(0x01)


        
        self.logger.debug("Opening device: {}".format(device_name))
        try:
            self.device = io.open(device_name, "r+b", buffering=0)
        except PermissionError as e:
            message = "Unable to open device: {}".format(device_name)
            raise InitializationError(message, logger=self.logger) from e

        # Verify device exists by trying to read from device
        try:
            byte = self.read(1)
        except ReadError as e:
            raise InitializationError("Unable to detect device") from e
        except MuxError as e:
            raise InitializationError("Unable to set mux") from e

        # Initialization successful!
        self.logger.debug("Successfully initialized")


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
        return False  # Don't suppress exceptions.


    @retry(WriteError, tries=5, delay=0.1, backoff=2) # type: ignore
    def write(self, byte_list: List[int], retry: bool = False) -> None:
        """Writes byte list to device. Converts byte list to byte array then 
        sends bytes. Returns error message. """

        # Set mux if enabled
        if self.mux != None:
            self.set_mux(self.mux, self.channel, retry=retry)

        # Build byte array and string
        byte_array = bytearray(byte_list)
        byte_string = "".join('0x{:02X} '.format(b) for b in byte_array)        

        # Write to i2c device
        self.logger.debug("Writing: {}".format(byte_string))
        try:    
            with threading.Lock():   
                fcntl.ioctl(self.device, self.I2C_SLAVE, self.address)
                self.device.write(byte_array)
        except IOError as e:
            raise WriteError("Unable to write to i2c device", byte_list) from e


    @retry(WriteError, tries=5, delay=0.1, backoff=2) # type: ignore
    def write_raw(self, bytes_: bytearray, retry: bool = False) -> None:
        """ Writes raw bytes to device. """

        # Set mux if enabled
        if self.mux != None:
            self.set_mux(self.mux, self.channel, retry=retry)        

        # Write raw to i2c device
        self.logger.debug("Writing raw: {}".format(bytes_))
        try:
            with threading.Lock():
                fcntl.ioctl(self.device, self.I2C_SLAVE, self.address)
                self.device.write(bytes_)
        except IOError as e:
            message = "Unable to write raw bytes: {}".format(bytes_)
            raise WriteError(message) from e


    @retry(ReadError, tries=5, delay=0.1, backoff=2) # type: ignore
    def read(self, num_bytes: int, retry: bool = False) -> bytearray:
        """ Reads num bytes from device. Returns byte array. """
        self.logger.debug("Reading {} bytes".format(num_bytes))

        # Set mux if enabled
        if self.mux != None:
            self.set_mux(self.mux, self.channel, retry=retry)

        # Read bytes
        try:
            with threading.Lock():
                fcntl.ioctl(self.device, self.I2C_SLAVE, self.address)
                raw_bytes = self.device.read(num_bytes)
                byte_array = bytearray(raw_bytes)
                byte_string = "".join('0x{:02X} '.format(b) for b in byte_array)
            self.logger.debug("Read: {}".format(byte_string))
            return byte_array
        except IOError as e:
            message = "Unable to read {} bytes".format(num_bytes)
            raise ReadError(message) from e


    @retry(ReadError, tries=5, delay=0.1, backoff=2) # type: ignore
    def read_raw(self, num_bytes: int, retry: bool = False) -> bytes:
        """Reads num bytes from device. Returns raw bytes."""

        # Set mux if enabled
        if self.mux != None:
            self.set_mux(self.mux, self.channel, retry=retry)

        # Read raw bytes
        try:
            with threading.Lock():
                fcntl.ioctl(self.device, self.I2C_SLAVE, self.address)
                bytes_ = self.device.read(num_bytes)
            self.logger.debug("Read raw: {}".format(bytes_))
            return bytes_
        except IOError as e:
            message = "Unable to read {} raw bytes".format(num_bytes)
            raise ReadError(message)


    @retry(ReadError, tries=5, delay=0.1, backoff=2) # type: ignore
    def read_register(self, address: int, retry: bool = False) -> int:
        """ Reads byte stored in register at address. """
        self.logger.debug("Reading register: 0x{:02X}".format(address))
        
        # Set mux if enabled
        if self.mux != None:
            self.set_mux(self.mux, self.channel, retry=retry)

        # Read register
        try:
            with threading.Lock():
                reg = c_uint8(address)
                result = c_uint8()
                request = make_i2c_rdwr_data([
                    (self.address, 0, 1, pointer(reg)), # write cmd register
                    (self.address, self.I2C_M_RD, 1, pointer(result)) # read 1 byte as result
                ])
                fcntl.ioctl(self.device.fileno(), self.I2C_RDWR, request)
                byte_ = result.value
            self.logger.debug("Register 0x{:02X}: 0x{:02X}".format(address, byte_))
            return byte_
        except IOError as e:
            message = "Unable to read register 0x{:02}".format(address)
            raise ReadError(message) from e


    @retry(MuxError, tries=5, delay=0.1, backoff=2) # type: ignore
    def set_mux(self, mux: int, channel: int, retry: bool = False) -> None:
        """ Sets mux to channel if enabled. """
        self.logger.debug("Setting mux 0x{:02X} to channel {}").format(mux, channel)

        # Build byte array and string
        channel_byte = 0x01 << channel
        byte_list = [channel_byte]
        byte_array = bytearray(byte_list)
        byte_string = "".join('0x{:02X} '.format(b) for b in byte_array)

        # Write to mux
        self.logger.debug("Writing to mux: 0x{:02X}".format(channel_byte))
        try:
            with threading.Lock():
                fcntl.ioctl(self.device, self.I2C_SLAVE, mux)
                self.device.write(byte_array)
        except IOError as e:
            raise MuxError("Unable to write to mux", mux, channel) from e


    def close(self) -> None:
        """ Closes device. """
        self.device.close()
