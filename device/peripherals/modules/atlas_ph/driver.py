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
from device.peripherals.modules.atlas_ph.exceptions import (
    SetupError,
    ReadPHError,
    SetCompensationTemperatureError,
    TakeCalibrationError,
    ClearCalibrationError,
)


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
            raise SetupError("Unable to setup", logger=self.logger) from e

    def read_ph(self, retry: bool = True) -> Optional[float]:
        """Reads potential hydrogen from sensor, sets significant 
        figures based off error magnitude."""
        self.logger.info("Reading pH")

        # Get potential hydrogen reading from hardware
        # Assumed potential hydrogen is only enabled output
        try:
            response = self.process_command("R", process_seconds=1.2, retry=retry)
        except Exception as e:
            message = "Unable to read pH"
            raise ReadPHError(message, logger=self.logger) from e

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

    def set_compensation_temperature(
        self, temperature: float, retry: bool = True
    ) -> None:
        """ Commands sensor to set compensation temperature. """
        self.logger.info("Setting compensation temperature")

        try:
            command = "T,{}".format(temperature)
            self.process_command(command, process_seconds=0.3, retry=retry)
        except Exception as e:
            message = "Unable to set compensation temperature"
            raise SetCompensationTemperatureError(message, logger=self.logger) from e

    def take_low_point_calibration_reading(
        self, value: float, retry: bool = True
    ) -> None:
        """Commands sensor to take a low point calibration reading."""
        self.logger.info("Taking low point calibration reading")

        try:
            command = "Cal,low,{}".format(value)
            self.process_command(command, process_seconds=0.9, retry=retry)
        except Exception as e:
            message = "Unable to take low point calibration"
            raise TakeCalibrationError(message, logger=self.logger) from e

    def take_mid_point_calibration_reading(
        self, value: float, retry: bool = True
    ) -> None:
        """ Commands sensor to take a mid point calibration reading. """
        self.logger.info("Taking mid point calibration reading")

        try:
            command = "Cal,mid,{}".format(value)
            self.process_command(command, process_seconds=0.9, retry=retry)
        except Exception as e:
            message = "Unable to take mid point calibration reading"
            raise TakeCalibrationError(message, logger=self.logger) from e

    def take_high_point_calibration_reading(
        self, value: float, retry: bool = True
    ) -> None:
        """ Commands sensor to take a high point calibration reading. """
        self.logger.info("Taking high point calibration reading")

        try:
            command = "Cal,high,{}".format(value)
            self.process_command(command, process_seconds=0.9, retry=retry)
        except Exception as e:
            message = "Unable to take high point calibration reading"
            raise TakeCalibrationError(message, logger=self.logger) from e

    def clear_calibration_readings(self, retry: bool = True) -> None:
        """ Commands sensor to clear calibration data. """
        self.logger.info("Clearing calibration readings")

        try:
            self.process_command("Cal,clear", process_seconds=0.3, retry=retry)
        except Exception as e:
            message = "Unable to clear claibration readings"
            raise ClearCalibrationError(message, logger=self.logger) from e
