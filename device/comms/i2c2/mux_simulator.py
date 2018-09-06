# Import standard python modules
from typing import Optional, Dict

# Import device utilities
from device.utilities.logger import Logger

# Import i2c package elements
from device.comms.i2c2.exceptions import MuxError


class MuxSimulator(object):
    """I2C mux simulator. Note connections is a dict because we could have multiple
    muxes on a device."""

    def __init__(self) -> None:
        self.logger = Logger(name="Simulator(Mux)", dunder_name=__name__)

    # Initialize mux parameters
    valid_channel_bytes = [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]
    connections: Dict[int, int] = {}

    def set(self, address: int, channel_byte: int) -> None:
        """Sets mux at address to channel."""
        message = "Setting addr 0x{:02X} to 0x{:02X}".format(address, channel_byte)
        self.logger.debug(message)

        # Verify valid channel byte:
        if channel_byte not in self.valid_channel_bytes:
            message = "Unable to set mux, invalid channel byte: 0x{:02X}".format(
                channel_byte
            )
            raise MuxError(message)

        # Set mux to channel
        self.connections[address] = channel_byte

        self.logger.debug("self.connections = {}".format(self.connections))

    def verify(self, address: int, channel: int) -> None:
        """Verifies if mux at address is set to correct channel."""
        self.logger.debug("Verifying mux connection")

        # Check mux exists
        if address not in self.connections:
            message = "Mux 0x{:02X} has never been set".format(address)
            raise MuxError(message, logger=self.logger)

        # Convert channel to channel byte
        channel_byte = 0x01 << channel
        if self.connections[address] != channel_byte:
            message = "Mux channel mismatch, stored: 0x{:02X}, received: 0x{:02X}".format(
                self.connections[address], channel_byte
            )
            raise MuxError(message, logger=self.logger)
