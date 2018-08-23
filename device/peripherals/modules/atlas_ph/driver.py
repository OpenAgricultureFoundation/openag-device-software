# Import standard python modules
import time
from typing import Optional, Tuple, NamedTuple

# Import device comms
from device.comms.i2c2.main import I2C
from device.comms.i2c2.exceptions import I2CError
from device.comms.i2c2.mux_simulator import MuxSimulator

# Import device utilities
from device.utilities.logger import Logger
from device.utilities import maths

# Import module elements
from device.peripherals.classes.atlas.driver import AtlasDriver
from device.peripherals.modules.atlas_ph.simulator import AtlasPHSimulator
from device.peripherals.modules.atlas_ph.exceptions import ReadPHError
from device.peripherals.classes.atlas.exceptions import SetupError


class AtlasPHDriver(AtlasDriver):  # type: ignore
    """Driver for Atlas pH sensor."""

    # Initialize sensor properties
    ph_accuracy = 0.002
    min_ph = 0.001
    max_ph = 14.000

    def __init__(
        self,
        name: str,
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
            Simulator = AtlasPHSimulator
        else:
            Simulator = None

        # Initialize parent class
        super().__init__(
            name=name,
            bus=bus,
            address=address,
            mux=mux,
            channel=channel,
            simulate=simulate,
            mux_simulator=mux_simulator,
            Simulator=Simulator,
        )

    def setup(self) -> None:
        """Sets up sensor."""
        self.logger.info("Setting up sensor")
        try:
            self.enable_led()
            info = self.read_info()
            if info.firmware_version > 1.94:
                self.enable_protocol_lock()
        except Exception as e:
            raise SetupError(logger=self.logger) from e

    def read_ph(self, retry: bool = True) -> Optional[float]:
        """Reads potential hydrogen from sensor, sets significant 
        figures based off error magnitude."""
        self.logger.info("Reading pH")

        # Get potential hydrogen reading from hardware
        # Assumed potential hydrogen is only enabled output
        try:
            response = self.process_command("R", process_seconds=1.2, retry=retry)
        except Exception as e:
            raise ReadPHError(logger=self.logger) from e

        # Process response
        ph_raw = float(response)

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
