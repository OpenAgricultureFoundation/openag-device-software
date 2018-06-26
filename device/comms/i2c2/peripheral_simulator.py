# Import standard python modules
from typing import Optional, Dict, Type, TypeVar, Callable, Any, cast
from types import TracebackType

# Import device utilities
from device.utilities.logger import Logger

# Import i2c package elements
from device.comms.i2c2.exceptions import InitError, WriteError, ReadError, MuxError
from device.comms.i2c2.mux_simulator import MuxSimulator

# Initialize type checking variables
F = TypeVar("F", bound=Callable[..., Any])
ET = TypeVar("ET", bound=Optional[Type[BaseException]])
EV = TypeVar("EV", bound=Optional[BaseException])
EB = TypeVar("ET", bound=Optional[TracebackType])


def verify_mux(func: F) -> F:
    """Verifies mux set to correct channel."""

    def wrapper(*args, **kwds):
        self = args[0]
        if self.mux_address != None:
            self.mux_simulator.verify(self.mux_address, self.mux_channel)
        return func(*args, **kwds)

    return cast(F, wrapper)


class PeripheralSimulator:
    """I2C peripheral simulator. 

    Attributes:
        name -- name of device
        bus --  device bus
        device_address -- device address
        mux_address -- device mux address
        mux_channel -- device mux channel
        mux_simulator -- mux simulator
    """

    def __init__(
        self,
        name: str,
        bus: int,
        device_address: int,
        mux_address: Optional[int],
        mux_channel: Optional[int],
        mux_simulator: Optional[MuxSimulator],
    ) -> None:

        # Initialize parameters
        self.name = name
        self.bus = bus
        self.device_address = device_address
        self.mux_address = mux_address
        self.mux_channel = mux_channel
        self.mux_simulator = mux_simulator

        # Initialize logger
        self.logger = Logger(name="Simulator({})".format(name), dunder_name=__name__)

        # Initialize buffer
        self.buffer: bytearray = bytearray([])  # mutable bytes

        # Initialize register
        self.register: Dict[int, int] = {}

    def __enter__(self) -> object:
        """Context manager enter function."""
        return self

    def __exit__(self, exc_type: ET, exc_val: EV, exc_tb: EB) -> bool:
        """Context manager exit function, ensures resources are cleaned up."""
        return False  # Don't suppress exceptions

    @verify_mux
    def read(self, address: int, num_bytes: int) -> bytes:
        """Reads bytes from buffer. Returns 0x00 if buffer is empty."""
        self.logger.debug("Reading {} bytes".format(num_bytes))
        self.logger.debug("buffer = {}".format(self.buffer))

        # Check device address matches
        if address != self.device_address:
            message = "Address not found: 0x{:02X}".format(address)
            raise ReadError(message)

        # Pop bytes from buffer and return
        bytes_ = []
        while num_bytes > 0:

            # Check for empty buffer or pop byte from buffer
            if len(self.buffer) == 0:
                bytes_.append(0x00)
            else:
                bytes_.append(self.buffer.pop())

            # Decrement num bytes to read
            num_bytes = num_bytes - 1

        # Successfully read bytes!
        return bytes_

    def write(self, address: int, bytes_: bytes) -> None:
        """Writes bytes to buffer."""

        # Check if writing to mux
        if address == self.mux_address:

            # Check if mux command valid
            if len(bytes_) > 1:
                raise MuxError("Unable to set mux, only 1 command byte is allowed")

            # Set mux to channel
            self.mux_simulator.set(self.mux_address, bytes_[0])

        # Check if writing to device
        elif address == self.device_address:

            # Verify mux connection
            if self.mux_address != None:
                self.mux_simulator.verify(self.mux_address, self.mux_channel)

            # Write bytes to buffer
            for byte in bytes_:
                self.buffer.insert(0, byte)
            self.logger.debug("buffer = {}".format(self.buffer))

        # Check for invalid address
        else:
            message = "Address not found: 0x{:02X}".format(address)
            raise WriteError(message)

    @verify_mux
    def read_register(self, address: int, register: int) -> int:
        """Reads register byte."""

        # Check address matches
        if address != self.device_address:
            message = "Address not found: 0x{:02X}".format(address)
            raise ReadError(message)

        # Check register within range
        if register not in range(256):
            message = "Invalid register addrress: {}, must be 0-255".format(register)
            raise ReadError(message)

        # Read register value from register dict
        try:
            return self.register[register]
        except KeyError:
            message = "Register not found: 0x{:02X}".format(register)
            raise ReadError(message)

    @verify_mux
    def write_register(self, address: int, register: int, value: int) -> None:
        """Writes byte to register."""

        # Check address matches
        if address != self.device_address:
            message = "Address not found: 0x{:02X}".format(address)
            raise WriteError(message)

        # Check register within range
        if register not in range(256):
            message = "Invalid register addrress: {}, must be 0-255".format(register)
            raise WriteError(message)

        # Check value within range
        if value not in range(256):
            message = "Invalid register value: {}, must be 0-255".format(value)
            raise WriteError(message)

        # Write value to register
        self.register[register] = value
