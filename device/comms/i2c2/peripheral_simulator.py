# Import standard python modules
from typing import Optional, Dict, Type
from types import TracebackType

# Import device utilities
from device.utilities.logger import Logger

# Import i2c package elements
from device.comms.i2c2.exceptions import InitializationError, WriteError, ReadError, MuxError
from device.comms.i2c2.mux_simulator import MuxSimulator
from device.comms.i2c2.utilities import I2CConfig


class PeripheralSimulator:
    """I2C peripheral simulator. 

    Attributes:
        name -- name of device
        bus --  device bus
        address -- device address
        mux -- device mux address
        channel -- device mux channel
        mux_simulator -- mux simulator
    """

    def __init__(self, config: I2CConfig) -> None:

        # Initialize parameters
        self.name = config.name
        self.bus = config.bus
        self.address = config.address
        self.mux = config.mux
        self.channel = config.channel
        self.mux_simulator = config.mux_simulator

        # Initialize logger
        self.logger = Logger(
            name = "Simulator({})".format(self.name),
            dunder_name = __name__,
        )

        # Initialize buffer
        self.buffer: bytearray = bytearray([]) # mutable bytes

        # Initialize register 
        self.register: Dict[int, int] = {}


    def __enter__(self) -> object:
        """Context manager enter function."""
        return self


    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], 
        exc_tb: Optional[TracebackType]) -> bool:
        """Context manager exit function, ensures resources are cleaned up."""
        return False  # Don't suppress exceptions


    def read(self, address: int, num_bytes: int) -> bytes:
        """Reads bytes from buffer. Returns 0x00 if buffer is empty."""
        self.logger.debug("Reading {} bytes".format(num_bytes))

        # Verify mux is on correct channel
        if self.mux != None:
            self.mux_simulator.verify(self.mux, self.channel)

        # Check address matches
        if address != self.address:
            message ="Address not found: 0x{:02X}".format(address)
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
            num_bytes = num_bytes -1

        # Successfully read bytes!
        return bytes_


    def write(self, address: int, bytes_: bytes) -> None:
        """Writes bytes to buffer."""

        # Check if writing to mux
        if address == self.mux:

            # Check if mux command valid
            print("bytes_ = {}".format(bytes_))
            if len(bytes_) > 1:
                raise MuxError("Unable to set mux, only 1 command byte is allowed")

            # Set mux to channel
            self.mux_simulator.set(self.mux, bytes_[0])
        
        # Check if writing to peripheral
        elif address == self.address: 

            # Write bytes to buffer
            for byte in bytes_:
                self.buffer.insert(0, byte)

        # Check for invalid address
        else: 
            message ="Address not found: 0x{:02X}".format(address)
            raise WriteError(message)


    def read_register(self, address: int, register: int) -> int:
        """Reads register byte."""

        # Verify mux is on correct channel
        if self.mux != None:
            self.mux_simulator.verify(self.mux, self.channel)

        # Check address matches
        if address != self.address:
            message ="Address not found: 0x{:02X}".format(address)
            raise ReadError(message)

        # Check register within range
        if register not in range(256):
            message = "Invalid register addrress: {}, must be 0-255".format(register)
            raise ReadError(message)

        # Read register value from register dict
        try:
            return self.register[register]
        except KeyError:
            message ="Register not found: 0x{:02X}".format(register)
            raise ReadError(message)


    def write_register(self, address: int, register: int, value: int) -> None:
        """Writes byte to register."""

        # Verify mux is on correct channel
        if self.mux != None:
            self.mux_simulator.verify(self.mux, self.channel)

        # Check address matches
        if address != self.address:
            message ="Address not found: 0x{:02X}".format(address)
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
