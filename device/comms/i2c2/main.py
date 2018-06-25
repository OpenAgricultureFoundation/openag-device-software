# Import standard python libraries
import fcntl, io, time, logging, threading, struct
from typing import Optional, List

# Import package elements
from device.comms.i2c2.device_io import DeviceIO
from device.comms.i2c2.utilities import make_i2c_rdwr_data, manage_mux
from device.comms.i2c2.utilities import I2CConfig as Config
from device.comms.i2c2.peripheral_simulator import PeripheralSimulator as Simulator
from device.comms.i2c2.exceptions import InitError, WriteError, ReadError, MuxError

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.functiontools import retry


class I2C(object):
    """I2C communication device. Can communicate with device directly or 
    via an I2C mux.

    Attributes:
        config -- config data
        Simulator -- io simulator class
    """

    def __init__(self, config: Config, Simulator: Optional[Simulator] = None) -> None:

        # Initialize passed in parameters
        self.name = config.name
        self.bus = config.bus
        self.address = config.address
        self.mux = config.mux
        self.channel = config.channel

        # Initialize logger instance
        logger_name = "I2C({})".format(self.name)
        self.logger = Logger(name=logger_name, dunder_name=__name__)
        self.logger.info("Initializing communication")

        # Verify mux config
        if self.mux != None and self.channel == None:
            raise InitError("Mux requires channel value to be set") from ValueError

        # Initialize io
        if Simulator != None:
            self.logger.info("Using simulated IO")
            self.io = Simulator(config)  # type: ignore
        else:
            self.logger.info("Using physical IO")
            self.io = DeviceIO(config)

        # Verify device exists
        try:
            self.logger.info("Verifying device exists")
            byte = self.read(1, retry=True)
        except ReadError as e:
            message = "Unable to verify device exists, read error"
            raise InitError(message, logger=self.logger) from e
        except MuxError as e:
            message = "Unable to verify device exists, mux error"
            raise InitError(message, logger=self.logger) from e

    @manage_mux
    @retry(WriteError, tries=5, delay=0.1, backoff=2)
    def write(self, bytes_: bytes, retry: bool = False) -> None:
        """Writes byte list to device. Converts byte list to byte array then 
        sends bytes. Returns error message."""
        self.logger.debug("Writing bytes: {}".format(bytes_))
        self.io.write(self.address, bytes_)

    @manage_mux
    @retry(ReadError, tries=5, delay=0.1, backoff=2)
    def read(self, num_bytes: int, retry: bool = False) -> bytearray:
        """Reads num bytes from device. Returns byte array."""
        self.logger.debug("Reading {} bytes".format(num_bytes))
        bytes_ = self.io.read(self.address, num_bytes)
        self.logger.debug("Read bytes: {}".format(bytes_))
        return bytes_

    @manage_mux
    @retry(ReadError, tries=5, delay=0.1, backoff=2)
    def read_register(self, register: int, retry: bool = False) -> int:
        """ Reads byte stored in register at address. """
        self.logger.debug("Reading register: 0x{:02X}".format(register))
        return self.io.read_register(self.address, register)

    @manage_mux
    @retry(WriteError, tries=5, delay=0.1, backoff=2)
    def write_register(self, register: int, value: int, retry: bool = False) -> None:
        message = "Writing register: 0x{:02X} value: 0x{:02X}".format(register, value)
        self.logger.debug(message)
        self.io.write_register(self.address, register, value)

    @retry(MuxError, tries=5, delay=0.1, backoff=2)
    def set_mux(self, mux: int, channel: int, retry: bool = False) -> None:
        """ Sets mux to channel if enabled. """
        self.logger.debug("Setting mux 0x{:02X} to channel {}".format(mux, channel))
        channel_byte = 0x01 << channel
        self.io.write(mux, bytes([channel_byte]))
