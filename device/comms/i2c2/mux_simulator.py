# Import standard python modules
from typing import Optional, Dict

# Import device utilities
from device.utilities.logger import Logger

# Import i2c package elements
from device.comms.i2c2.exceptions import MuxError


class MuxSimulator(object):
    """I2C mux simulator."""


    def __init__(self):
        self.logger = Logger(
            name = "MuxSimulator",
            dunder_name = __name__,
        )

    # Initialize mux parameters
    valid_channel_bytes = [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]
    connections = {}


    def set(self, address: int, channel_byte: int) -> None:
        """Sets mux at address to channel."""
        self.logger.debug("Setting addr 0x{:02X} to 0x{:02X}".format(address, channel_byte))

        # Verify valid channel byte:
        if channel_byte not in self.valid_channel_bytes:
            message = "Unable to set mux, invalid channel byte: 0x{:02X}".format(channel_byte)
            raise MuxError(message)

        # Set mux to channel
        self.connections[address] = channel_byte

        self.logger.debug("Successfully set mux")


    def verify(self, address: int, channel: int) -> None:
        """Verifies if mux at address is set to correct channel."""
        self.logger.debug("Verifying mux address is set to channel")

        # Check mux exists
        if address not in self.connections:
            message = "Mux 0x{:02X} has never been set".format(address)
            raise MuxError(message, logger=self.logger)

        # Convert channel to channel byte
        channel_byte = 0x01 << channel
        if self.connections[address] != channel_byte:
            message = "Mux channel mismatch, stored: 0x{:02X}, received: 0x{:02X}".format(
                self.connections[address], channel_byte)
            raise MuxError(message, logger=self.logger)

        # Successfully verified!
        self.logger.debug("Mux address/channel verified!")
