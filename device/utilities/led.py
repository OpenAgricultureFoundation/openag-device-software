# Utility class to control the RGB LED built into the v6 CNS and v5 EDU boards.
# The LED is controlled by a PCA9632 I2C chip.
# https://www.nxp.com/docs/en/data-sheet/PCA9632.pdf
# https://github.com/JohnnyTheOne/MarlinAnetA6/blob/master/pca9632.cpp

# Import standard python modules
import time, threading

# Import python types
from typing import NamedTuple, Optional, Dict

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.communication.i2c.main import I2C
from device.utilities.communication.i2c.exceptions import I2CError
from device.utilities.communication.i2c.mux_simulator import MuxSimulator
from device.utilities.exceptions import ExceptionLogger

class LEDError(ExceptionLogger):
    pass


class LED:
    # --------------------------------------------------------------------------
    # Constants for PCA9632
    PCA9632_I2C_ADDRESS=0x62
    R_BYTE=3
    G_BYTE=4
    B_BYTE=5

    # --------------------------------------------------------------------------
    def __init__(
        self,
        bus: int = 0,
        address: int = PCA9632_I2C_ADDRESS,
        mux: Optional[int] = None,
        channel: Optional[int] = None,
        simulate: bool = False,
        mux_simulator: Optional[MuxSimulator] = None,
    ) -> None:
        """Initializes Grove RGB LCD."""

        # Initialize logger
        self.logger = Logger('LED', __name__)

        # Check if simulating
        if simulate:
            self.logger.info("Simulating LED")

        # Initialize I2C
        try:
            self.i2c = I2C(
                name="LED",
                i2c_lock= threading.RLock(),
                bus=bus,
                address=address,
                mux=mux,
                channel=channel,
                mux_simulator=mux_simulator,
                PeripheralSimulator=None,
            )
        except I2CError as e:
            raise LEDError(logger=self.logger) from e

        # Initialize the LED
        try:
            self.init_data = [
                    0x80, 0x80, 0x21, 0x00, 0x00, 0x00, 0x40, 0x80, 0x02, 0xEA]

            # init and clear any LED values
            self.i2c.write(bytes(self.init_data))

        except I2CError as e:
            raise LEDError(logger=self.logger) from e

    # --------------------------------------------------------------------------
    # Turn off all LEDs
    def off(self):
        try:
            data = self.init_data
            data[self.R_BYTE] = 0x00 
            data[self.G_BYTE] = 0x00 
            data[self.B_BYTE] = 0x00 
            self.i2c.write(bytes(data))

        except I2CError as e:
            raise LEDError(logger=self.logger) from e
    
    # --------------------------------------------------------------------------
    def set(self, R: int = 0x00, G: int = 0x00, B: int = 0x00) -> None:
        # validate the inputs are 0 <> 255
        if R < 0 or R > 255 or G < 0 or G > 255 or B < 0 or B > 255:
            self.logger.error("RGB values must be between 0 and 255")
            raise LEDError(logger=self.logger)

        message = "Setting LED: {:2X}, {:2X}, {:2X}".format(R, G, B)
        self.logger.debug(message)

        # Set the backlight RGB value
        try:
            data = self.init_data
            data[self.R_BYTE] = R
            data[self.G_BYTE] = G
            data[self.B_BYTE] = B
            self.i2c.write(bytes(data))
        except I2CError as e:
            raise LEDError(logger=self.logger) from e


