# Import standard python modules
import time, threading

# Import python types
from typing import Optional, Tuple, NamedTuple

# Import device utilities
from device.utilities import maths
from device.utilities.communication.i2c.main import I2C
from device.utilities.communication.i2c.exceptions import I2CError
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

# Import module elements
from device.peripherals.classes.atlas import driver
from device.peripherals.modules.atlas_ph import simulator, exceptions


class AtlasPHDriver(driver.AtlasDriver):
    """Driver for Atlas pH sensor."""

    # Initialize sensor properties
    ph_accuracy = 0.002
    min_ph = 0.001
    max_ph = 14.000

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
        """ Initializes driver. """

        # Check if simulating
        if simulate:
            Simulator = simulator.AtlasPHSimulator
        else:
            Simulator = None

        # Initialize parent class
        super().__init__(
            name=name,
            i2c_lock=i2c_lock,
            bus=bus,
            address=address,
            mux=mux,
            channel=channel,
            simulate=simulate,
            mux_simulator=mux_simulator,
            Simulator=Simulator,
        )

    def setup(self, retry: bool = True) -> None:
        """Sets up sensor."""
        self.logger.info("Setting up sensor")
        try:
            self.enable_led(retry=retry)
            info = self.read_info(retry=retry)
            if info.firmware_version > 1.94:
                self.enable_protocol_lock(retry=retry)
        except Exception as e:
            raise exceptions.SetupError(logger=self.logger) from e

    def read_ph(self, retry: bool = True) -> Optional[float]:
        """Reads potential hydrogen from sensor, sets significant 
        figures based off error magnitude."""
        self.logger.info("Reading pH")

        # Get potential hydrogen reading from hardware
        # Assumed potential hydrogen is only enabled output
        try:
            response = self.process_command("R", process_seconds=2.4, retry=retry)
        except Exception as e:
            raise exceptions.ReadPHError(logger=self.logger) from e

        # Process response
        ph_raw = float(response)  # type: ignore

        # Set significant figures based off error magnitude
        error_magnitude = maths.magnitude(self.ph_accuracy)
        significant_figures = error_magnitude * -1
        ph = round(ph_raw, significant_figures)

        # Verify pH value within valid range
        if ph < self.min_ph or ph > self.max_ph:
            self.logger.warning("pH outside of valid range")
            return None

        # Succesfully read pH
        self.logger.info("pH: {}".format(ph))
        return ph
