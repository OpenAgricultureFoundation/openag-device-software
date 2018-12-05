# Import standard python modules
import logging

# Import python types
from typing import Optional, Dict, Type, TypeVar, Callable, Any, cast
from types import TracebackType

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.bitwise import byte_str

# Import i2c package elements
from device.utilities.communication.i2c.exceptions import (
    InitError,
    WriteError,
    ReadError,
    MuxError,
)
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

# Initialize type checking variables
F = TypeVar("F", bound=Callable[..., Any])
ET = TypeVar("ET", bound=Optional[Type[BaseException]])
EV = TypeVar("EV", bound=Optional[BaseException])
EB = TypeVar("EB", bound=Optional[TracebackType])


def verify_mux(func: F) -> F:
    """Verifies mux set to correct channel."""

    def wrapper(*args, **kwds):  # type: ignore
        self = args[0]
        if self.mux_address != None:
            self.mux_simulator.verify(self.mux_address, self.mux_channel)
        return func(*args, **kwds)

    return cast(F, wrapper)


class PeripheralSimulator:
    """I2C peripheral simulator base class."""

    def __init__(
        self,
        name: str,
        bus: int,
        device_addr: int,
        mux_address: Optional[int],
        mux_channel: Optional[int],
        mux_simulator: Optional[MuxSimulator],
    ) -> None:

        # Initialize parameters
        self.name = name
        self.bus = bus
        self.device_addr = device_addr
        self.mux_address = mux_address
        self.mux_channel = mux_channel
        self.mux_simulator = mux_simulator

        # Initialize logger
        logname = "Simulator({})".format(name)
        self.logger = Logger(logname, __name__)
        self.logger.debug("Initializing simulator")

        # Initialize buffer
        self.buffer: bytearray = bytearray([])  # mutable bytes

        # Initialize register
        self.registers: Dict[int, int] = {}
        self.writes: Dict[str, bytes] = {}

    def __enter__(self) -> object:
        """Context manager enter function."""
        return self

    def __exit__(self, exc_type: ET, exc_val: EV, exc_tb: EB) -> bool:
        """Context manager exit function, ensures resources are cleaned up."""
        return False  # Don't suppress exceptions

    @verify_mux
    def read(self, device_addr: int, num_bytes: int) -> bytes:
        """Reads bytes from buffer. Returns 0x00 if buffer is empty."""
        msg = "Reading {} bytes, buffer: {}".format(num_bytes, byte_str(self.buffer))
        self.logger.debug(msg)

        # Check device address matches
        if device_addr != self.device_addr:
            message = "Address not found: 0x{:02X}".format(device_addr)
            raise ReadError(message)

        return self.get_read_response_bytes(num_bytes)

    def write(self, address: int, bytes_: bytes) -> None:
        """Writes bytes to buffer."""

        # Check if writing to mux
        if address == self.mux_address:

            # Check if mux command valid
            if len(bytes_) > 1:
                raise MuxError("Unable to set mux, only 1 command byte is allowed")

            # Set mux to channel
            self.mux_simulator.set(self.mux_address, bytes_[0])  # type: ignore

        # Check if writing to device
        elif address == self.device_addr:

            # Verify mux connection
            if self.mux_address != None:
                address = self.mux_address  # type: ignore
                channel = self.mux_channel
                self.mux_simulator.verify(address, channel)  # type: ignore

            # Get response bytes
            response_bytes = self.get_write_response_bytes(bytes_)

            # Verify known write bytes
            if response_bytes == None:
                raise WriteError("Unknown write bytes: {}".format(byte_str(bytes_)))

            # Write response bytes to buffer
            response_byte_string = byte_str(response_bytes)  # type: ignore
            self.logger.debug("Response bytes: {}".format(response_byte_string))
            for byte in response_bytes:  # type: ignore
                self.buffer.insert(0, byte)
            self.logger.debug("Buffer: {}".format(byte_str(self.buffer)))

        # Check for invalid address
        else:
            message = "Address not found: 0x{:02X}".format(address)
            raise WriteError(message)

    @verify_mux
    def read_register(self, device_addr: int, register_addr: int) -> int:
        """Reads register byte."""

        # Check address matches
        if device_addr != self.device_addr:
            message = "Address not found: 0x{:02X}".format(device_addr)
            raise ReadError(message)

        # Check register within range
        if register_addr not in range(256):
            message = "Invalid register addrress: {}, must be 0-255".format(
                register_addr
            )
            raise ReadError(message)

        # Read register value from register dict
        try:
            return self.registers[register_addr]
        except KeyError:
            message = "Register address not found: 0x{:02X}".format(register_addr)
            raise ReadError(message)

    @verify_mux
    def write_register(self, device_addr: int, register_addr: int, value: int) -> None:
        """Writes byte to register."""

        # Check address matches
        if device_addr != self.device_addr:
            message = "Device address not found: 0x{:02X}".format(device_addr)
            raise WriteError(message)

        # Check register within range
        if register_addr not in range(256):
            message = "Invalid register addrress: {}, must be 0-255".format(
                register_addr
            )
            raise WriteError(message)

        # Check value within range
        if value not in range(256):
            message = "Invalid register value: {}, must be 0-255".format(value)
            raise WriteError(message)

        # Write value to register
        self.registers[register_addr] = value

    def get_write_response_bytes(self, write_bytes: bytes) -> Optional[bytes]:
        """Gets response byte for write command. Handles state based writes."""
        return self.writes.get(byte_str(write_bytes), None)

    def get_read_response_bytes(self, num_bytes: int) -> bytes:
        """Gets response bytes from read command. Handles state based reads."""

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

        # Successfully read bytes
        return bytes(bytes_)
