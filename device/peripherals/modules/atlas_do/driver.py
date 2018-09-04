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
from device.peripherals.modules.atlas_do.simulator import AtlasDOSimulator
from device.peripherals.modules.atlas_do.exceptions import (
    ReadDOError,
    EnableMgLOutputError,
    DisableMgLOutputError,
    EnablePercentSaturationOutputError,
    DisablePercentSaturationOutputError,
    SetCompensationECError,
    SetCompensationPressureError,
)
from device.peripherals.classes.peripheral.exceptions import SetupError


class AtlasDODriver(AtlasDriver):  # type: ignore
    """Driver for atlas dissolved oxygen sensor."""

    # Initialize sensor properties
    do_accuracy = 0.05  # mg/L
    min_do = 0.01
    max_do = 100

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
            Simulator = AtlasDOSimulator
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
            self.enable_mg_l()
            self.disable_percent_saturation()
        except Exception as e:
            raise SetupError(logger=self.logger) from e

    def read_do(self, retry: bool = True) -> Optional[float]:
        """Reads dissolved oxygen value."""
        self.logger.debug("Reading DO")

        # Get dissolved oxygen reading from hardware
        # Assumed dissolved oxygen is only enabled output
        try:
            response = self.process_command("R", process_seconds=0.6, retry=retry)
        except Exception as e:
            raise ReadDOError(logger=self.logger) from e

        # Parse response
        do_raw = float(response)

        # Set significant figures based off error magnitude
        error_magnitude = maths.magnitude(self.do_accuracy)
        significant_figures = error_magnitude * -1
        do = round(do_raw, significant_figures)

        # Verify dissolved oxygen value within valid range
        if do > self.min_do and do < self.min_do:
            self.logger.warning("Dissolved oxygen outside of valid range")
            return None

        # Successfully read dissolved oxygen
        self.logger.debug("DO: {}".format(do))
        return do

    def enable_mg_l_output(self, retry: bool = True) -> None:
        """Enables DO mg/L output."""
        self.logger.info("Enabling DO mg/L output")
        try:
            self.process_command("O,mg,1", process_seconds=0.3, retry=retry)
        except Exception as e:
            raise EnableMgLOutputError(logger=self.logger) from e

    def disable_mg_l_output(self, retry: bool = True) -> None:
        """Disables DO mg/L output."""
        self.logger.info("Disabling DO mg/L output")
        try:
            self.process_command("O,mg,0", process_seconds=0.3, retry=retry)
        except Exception as e:
            raise DisableMgLOutputError(logger=self.logger) from e

    def enable_percent_saturation_output(self, retry: bool = True) -> None:
        """Enables precent saturation output."""
        self.logger.info("Enabling percent saturation output")
        try:
            self.process_command("O,%,1", process_seconds=0.3, retry=retry)
        except Exception as e:
            raise EnablePercentSaturationOutputError(logger=self.logger) from e

    def disable_percent_saturation_output(self, retry: bool = True) -> None:
        """Disables percent saturation output."""
        self.logger.info("Disabling percent saturation output")
        try:
            self.process_command("O,%,0", process_seconds=0.3, retry=retry)
        except Exception as e:
            raise DisablePercentSaturationOutputError(logger=self.logger) from e

    def set_compensation_ec(self, value_ms_cm: float, retry: bool = True) -> None:
        """Sets compensation ec."""
        self.logger.info("Setting compensation ec")

        # Convert value to uS/Cm
        value_us_cm = value_ms_cm * 1000.0
        command = "S,{}".format(value_us_cm)

        # Send command
        try:
            self.process_command(command, process_seconds=0.3, retry=retry)
        except Exception as e:
            raise SetCompensationECError(logger=self.logger) from e

    def set_compensation_pressure(self, value: float, retry: bool = True) -> None:
        """Sets compensation ec."""
        self.logger.info("Setting compensation pressure")
        try:
            command = "P,{}".format(value)
            self.process_command(command, process_seconds=0.3, retry=retry)
        except Exception as e:
            raise SetCompensationPressureError(logger=self.logger) from e
