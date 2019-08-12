# Import standard python modules
import time, threading

# Import python types
from typing import NamedTuple, Optional, Dict

# Import device utilities
from device.utilities import bitwise, logger
from device.utilities.communication.i2c.main import I2C
from device.utilities.communication.i2c.exceptions import I2CError
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

# Import driver elements
from device.peripherals.common.pca9633.simulator import PCA9633Simulator
from device.peripherals.common.pca9633 import exceptions


class PCA9633Driver:
    """Driver for PCA9633 LED driver."""

    def __init__(
        self,
        name: str,
        i2c_lock: threading.RLock,
        bus: int,
        address: int,
        mux: Optional[int] = None,
        channel: Optional[int] = None,
        simulate: bool = False,
        mux_simulator: Optional[MuxSimulator] = None,
    ) -> None:
        """Initializes PCA9633."""

        # Initialize logger
        logname = "PCA9633({})".format(name)
        self.logger = logger.Logger(logname, "peripherals")

        # Initialize i2c lock
        self.i2c_lock = i2c_lock

        # Check if simulating
        if simulate:
            self.logger.info("Simulating driver")
            Simulator = PCA9633Simulator
        else:
            Simulator = None

        # Initialize driver parameters
        self.name = name

        # Initialize data bytes
        self.data_bytes = [0x80, 0x80, 0x21, 0x00, 0x00, 0x00, 0x40, 0x80, 0x02, 0xEA]

        # Initialize I2C
        try:
            self.i2c = I2C(
                name="PCA9633-{}".format(name),
                i2c_lock=i2c_lock,
                bus=bus,
                address=address,
                mux=mux,
                channel=channel,
                mux_simulator=mux_simulator,
                PeripheralSimulator=Simulator,
            )
            self.i2c.write(bytes(self.data_bytes), disable_mux=True)
        except I2CError as e:
            raise exceptions.InitError(logger=self.logger) from e

    def set_rgb(self, rgb: list, retry: bool = True, disable_mux: bool = False) -> None:
        """Sets port high."""
        self.logger.debug("Setting rgb: {}".format(rgb))

        # Check valid rgb list length
        if len(rgb) != 3:
            message = "rgb list not of length 3"
            raise exceptions.SetRgbError(message=message, logger=self.logger)

        # Check valid rgb value range
        if rgb[0] < 0 or rgb[0] > 255:
            message = "red value out of range, must be within 0-255"
            raise exceptions.SetRgbError(message=message, logger=self.logger)
        if rgb[1] < 0 or rgb[1] > 255:
            message = "green value out of range, must be within 0-255"
            raise exceptions.SetRgbError(message=message, logger=self.logger)
        if rgb[2] < 0 or rgb[2] > 255:
            message = "blue value out of range, must be within 0-255"
            raise exceptions.SetRgbError(message=message, logger=self.logger)

        # Lock thread in case we have multiple io expander instances
        with self.i2c_lock:

            # Update data bytes
            self.data_bytes[3] = rgb[0]  # Red
            self.data_bytes[4] = rgb[1]  # Green
            self.data_bytes[5] = rgb[2]  # Blue

            # Send set output command to ic
            try:
                self.i2c.write(bytes(self.data_bytes), disable_mux=disable_mux)
            except I2CError as e:
                raise exceptions.SetRgbError(logger=self.logger) from e
