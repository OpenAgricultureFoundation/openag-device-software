# Import standard python modules
from typing import Optional, Dict

# Import device utilities
from device.utilities.logger import Logger

# Import i2c package elements
from device.comms.i2c2.exceptions import InitializationError, WriteError, ReadError, MuxError


class Simulator:
    """I2C device simulator. 

    Attributes:
        name -- name of device
        bus --  device bus
        address -- device address
        mux -- device mux address
        channel -- device mux channel
    """


    def __init__(self, name: str, address: int, bus: int) -> None:

        # Initialize parameters
        self.name = name
        self.address = address
        self.bus = bus

        # Initialize logger
        self.logger = Logger(
            name = "Simulator({})".format(name),
            dunder_name = __name__,
        )

        # Initialize buffer
        self.buffer: bytearray = bytearray([]) # mutable bytes

        # Initialize register 
        self.register: Dict[int, int] = {}


    def read(self, address: int, num_bytes: int) -> bytes:
        """Reads bytes from buffer. Returns 0x00 if buffer is empty."""
        self.logger.debug("Reading {} bytes".format(num_bytes))

        # Check address matches
        if address != self.address:
            message ="Address not found: 0x{:02X}".format(address)
            raise WriteError(message)

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

        # Check address matches
        if address != self.address:
            message ="Address not found: 0x{:02X}".format(address)
            raise WriteError(message)

        # Insert bytes into buffer
        for byte in bytes_:
            self.buffer.insert(0, byte)


    def read_register(self, address: int, register: int) -> int:
        """Reads register byte."""

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
