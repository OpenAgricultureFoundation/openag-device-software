# Import standard python modules
import time, threading

# Import python types
from typing import Optional, Tuple, NamedTuple

# Import device utilities
from device.utilities.logger import Logger
from device.utilities import logger, maths

# from device.utilities.communication.i2c.main import I2C
# from device.utilities.communication.i2c.exceptions import I2CError
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

# Import driver elements
from device.peripherals.classes.atlas import driver
from device.peripherals.modules.atlas_do import simulator, exceptions


class AtlasDODriver(driver.AtlasDriver):
    """Driver for atlas dissolved oxygen sensor."""

    # Initialize sensor properties
    do_accuracy = 0.05  # mg/L
    min_do = 0.01
    max_do = 100

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
            Simulator = simulator.AtlasDOSimulator
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
            self.enable_mg_l_output(retry=retry)
            self.disable_percent_saturation_output(retry=retry)
        except Exception as e:
            raise exceptions.SetupError(logger=self.logger) from e

    def read_do(self, retry: bool = True) -> Optional[float]:
        """Reads dissolved oxygen value."""
        self.logger.debug("Reading DO")

        # Get dissolved oxygen reading from hardware
        # Assumed dissolved oxygen is only enabled output
        try:
            response = self.process_command("R", process_seconds=0.6, retry=retry)
        except Exception as e:
            raise exceptions.ReadDOError(logger=self.logger) from e

        # Parse response
        do_raw = float(response)  # type: ignore

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
            raise exceptions.EnableMgLOutputError(logger=self.logger) from e

    def disable_mg_l_output(self, retry: bool = True) -> None:
        """Disables DO mg/L output."""
        self.logger.info("Disabling DO mg/L output")
        try:
            self.process_command("O,mg,0", process_seconds=0.3, retry=retry)
        except Exception as e:
            raise exceptions.DisableMgLOutputError(logger=self.logger) from e

    def enable_percent_saturation_output(self, retry: bool = True) -> None:
        """Enables precent saturation output."""
        self.logger.info("Enabling percent saturation output")
        try:
            self.process_command("O,%,1", process_seconds=0.3, retry=retry)
        except Exception as e:
            raise exceptions.EnablePercentSaturationOutputError(
                logger=self.logger
            ) from e

    def disable_percent_saturation_output(self, retry: bool = True) -> None:
        """Disables percent saturation output."""
        self.logger.info("Disabling percent saturation output")
        try:
            self.process_command("O,%,0", process_seconds=0.3, retry=retry)
        except Exception as e:
            raise exceptions.DisablePercentSaturationOutputError(
                logger=self.logger
            ) from e

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
            raise exceptions.SetCompensationECError(logger=self.logger) from e

    def set_compensation_pressure(self, value: float, retry: bool = True) -> None:
        """Sets compensation ec."""
        self.logger.info("Setting compensation pressure")
        try:
            command = "P,{}".format(value)
            self.process_command(command, process_seconds=0.3, retry=retry)
        except Exception as e:
            raise exceptions.SetCompensationPressureError(logger=self.logger) from e
