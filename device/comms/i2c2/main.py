# Import standard python libraries
import fcntl, io, time, logging, threading, struct
from typing import Optional, List, Any, Callable, TypeVar, Tuple, cast, NamedTuple

# Import package elements
from device.comms.i2c2.device_io import DeviceIO
from device.comms.i2c2.utilities import make_i2c_rdwr_data
from device.comms.i2c2.utilities import I2CConfig as Config
from device.comms.i2c2.peripheral_simulator import PeripheralSimulator as Simulator
from device.comms.i2c2.exceptions import (
    InitializationError,
    WriteError,
    ReadError,
    MuxError,
)

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.functiontools import retry

# Initialize function type variable for decorator type checking
FuncType = Callable[..., Any]
F = TypeVar("F", bound=FuncType)


def manage_mux(f):

    def wrapper(*args, **kwargs):
        self = args[0]
        if self.mux != None:
            self.set_mux(self.mux, self.channel)
        return f(*args, **kwargs)

    return wrapper


class I2C(object):
    """I2C communication device. Can communicate with device directly or 
    via an I2C mux.

    Attributes:
        config -- config dataclass instance
        Simulator -- peripheral simulator class
    """

    def __init__(self, config: Config, Simulator: Optional[Simulator] = None) -> None:

        # Initialize passed in parameters
        self.config = config
        self.name = config.name
        self.bus = config.bus
        self.address = config.address
        self.mux = config.mux
        self.channel = config.channel

        # Initialize logger instance
        logger_name = "I2C({})".format(self.name)
        self.logger = Logger(name=self.name, dunder_name=__name__)

        # Verify mux config
        if self.mux != None and self.channel == None:
            raise InitializationError("Mux requires channel to be set")

        # Initialize I2CIO class
        if Simulator != None:
            self.I2CIO = self.get_simulator(Simulator)
        else:
            self.I2CIO = DeviceIO

        # Verify device exists
        try:
            if self.mux != None:
                self.set_mux(self.mux, self.channel, retry=True)
            byte = self.read(1, retry=True)
        except ReadError as e:
            raise InitializationError("Unable to detect device") from e
        except MuxError as e:
            self.logger.exception("Unable to set mux")
            raise InitializationError("Unable to set mux") from e

        # Initialization successful!
        self.logger.debug("Successfully initialized")

    def get_simulator(self, Simulator: Simulator) -> Simulator:
        """Gets callable simulator in type-checkable way. TODO: Clean up this method. """
        return Simulator

    # @retry(WriteError, tries=5, delay=0.1, backoff=2) # type: ignore
    @manage_mux
    def write(self, bytes_: bytes, retry: bool = False) -> None:
        """Writes byte list to device. Converts byte list to byte array then 
        sends bytes. Returns error message."""

        # # Set mux if enabled
        # if self.mux != None:
        #     self.set_mux(self.mux, self.channel, retry=retry)

        # Write to i2c device
        self.logger.debug("Writing: {}".format(bytes_))
        with self.I2CIO(self.config) as io:
            io.write(self.address, bytes_)

    @retry(ReadError, tries=5, delay=0.1, backoff=2)
    def read(self, num_bytes: int, retry: bool = False) -> bytearray:
        """ Reads num bytes from device. Returns byte array. """

        # # Set mux if enabled
        # if self.mux != None:
        #     self.set_mux(self.mux, self.channel, retry=retry)

        # Read bytes
        self.logger.debug("Reading {} bytes".format(num_bytes))
        with self.I2CIO(self.config) as io:
            return io.read(self.address, num_bytes)

    @retry(ReadError, tries=5, delay=0.1, backoff=2)  # type: ignore
    def read_register(self, register: int, retry: bool = False) -> int:
        """ Reads byte stored in register at address. """

        # # Set mux if enabled
        # if self.mux != None:
        #     self.set_mux(self.mux, self.channel, retry=retry)

        # Read register
        self.logger.debug("Reading register: 0x{:02X}".format(register))
        with self.I2CIO(self.config) as io:
            return io.read_register(self.address, register)

    @retry(ReadError, tries=5, delay=0.1, backoff=2)  # type: ignore
    def write_register(self, register: int, value: int, retry: bool = False) -> int:
        """ Writes byte to register."""

        # # Set mux if enabled
        # if self.mux != None:
        #     self.set_mux(self.mux, self.channel, retry=retry)

        # Write register
        self.logger.debug(
            "Writing register: 0x{:02X} value: 0x{:02X}".format(register, value)
        )
        with self.I2CIO(self.config) as io:
            return io.write_register(self.address, register, value)

    @retry(MuxError, tries=5, delay=0.1, backoff=2)  # type: ignore
    def set_mux(self, mux: int, channel: int, retry: bool = False) -> None:
        """ Sets mux to channel if enabled. """

        self.logger.debug("Setting mux 0x{:02X} to channel {}".format(mux, channel))

        # Set channel byte
        channel_byte = 0x01 << channel

        # Write to mux
        self.logger.debug("Writing to mux: 0x{:02X}".format(channel_byte))
        with self.I2CIO(self.config) as io:
            io.write(mux, bytes([channel_byte]))
