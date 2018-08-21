# Import standard python modules
import time
from typing import Optional, Tuple, NamedTuple

# Import device comms
from device.comms.i2c2.main import I2C
from device.comms.i2c2.exceptions import I2CError

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error
from device.utilities import maths

# Import parent class
from device.peripherals.classes.atlas_driver import AtlasDriver

# Import simulator
from device.peripherals.modules.atlas_ph.simulator import AtlasPHSimulator


class AtlasPHDriver(AtlasDriver):
    """Driver for Atlas pH sensor."""

    # Initialize sensor properties
    _potential_hydrogen_accuracy = 0.002
    _min_potential_hydrogen = 0.001
    _max_potential_hydrogen = 14.000

    def __init__(
        self,
        name: str,
        bus: int,
        address: int,
        mux: Optional[int] = None,
        channel: Optional[int] = None,
        simulate: bool = False,
    ) -> None:
        """ Initializes driver. """

        super().__init__(
            name=name,
            bus=bus,
            address=address,
            mux=mux,
            channel=channel,
            logger_name="Driver({})".format(name),
            dunder_name=__name__,
            simulate=simulate,
            Simulator=AtlasPHSimulator,
        )

    def read_potential_hydrogen(self) -> Tuple[Optional[float], Error]:
        """ Reads potential hydrogen from sensor, sets significant 
            figures based off error magnitude. """
        self.logger.debug("Reading potential hydrogen")

        # Get potential hydrogen reading from hardware
        # Assumed potential hydrogen is only enabled output
        response, error = self.process_command("R", processing_seconds=1.2)  # was 0.6

        # Check for errors
        if error.exists():
            error.report("Driver unable to read potential hydrogen")
            self.logger.error(error.summary())
            return None, error

        # Process response
        potential_hydrogen_raw = float(response)

        # Set significant figures based off error magnitude
        error_magnitude = maths.magnitude(self._potential_hydrogen_accuracy)
        significant_figures = error_magnitude * -1
        potential_hydrogen = round(potential_hydrogen_raw, significant_figures)

        # Verify potential hydrogen value within valid range
        if (
            potential_hydrogen > self._min_potential_hydrogen
            and potential_hydrogen < self._min_potential_hydrogen
        ):
            self.logger.warning("Potential hydrogen outside of valid range")
            potential_hydrogen = None

        # Succesfully read pH!
        self.logger.info("pH: {}".format(potential_hydrogen))
        return potential_hydrogen, Error(None)

    def set_compensation_temperature(self, temperature: float) -> Error:
        """ Commands sensor to set compensation temperature. """
        self.logger.info("Setting compensation temperature")

        # Send command
        command = "T,{}".format(temperature)
        _, error = self.process_command(command, processing_seconds=0.3)

        # Check for error
        if error.exists():
            error.report("Driver unable to set compensation temperature")
            self.logger.error(error.summary())
            return error

        # Successfully set compensation temperature!
        return Error(None)

    def take_low_point_calibration_reading(self, value: float) -> Error:
        """ Commands sensor to take a low point calibration reading. """
        self.logger.info("Taking low point calibration reading")

        # Send take low point calibration command to hardware
        command = "Cal,low,{}".format(value)
        _, error = self.process_command(command, processing_seconds=0.9)

        # Check for errors
        if error.exists():
            error.report("Driver unable to take low point calibration reading")
            self.logger.error(error.summary())
            return error

        # Succesfully took low point calibration reading
        return Error(None)

    def take_mid_point_calibration_reading(self, value: float) -> Error:
        """ Commands sensor to take a mid point calibration reading. """
        self.logger.info("Taking mid point calibration reading, value={}".format(value))

        # Send take mid point calibration command to hardware
        command = "Cal,mid,{}".format(value)
        _, error = self.process_command(command, processing_seconds=0.9)

        # Check for errors
        if error.exists():
            error.report("Driver unable to take mid point calibration reading")
            self.logger.error(error.summary())
            return error

        # Successfully took mid point calibration reading!
        return Error(None)

    def take_high_point_calibration_reading(self, value: float) -> Error:
        """ Commands sensor to take a high point calibration reading. """
        self.logger.info("Taking high point calibration reading")

        # Send take high point calibration command to hardware
        command = "Cal,high,{}".format(value)
        _, error = self.process_command(command, processing_seconds=0.9)

        # Check for errors
        if error.exists():
            error.report("Driver unable to take high point calibration reading")
            self.logger.error(error.summary())
            return error

        # Successfully took high point calibration reading!
        return Error(None)

    def clear_calibration_readings(self) -> Error:
        """ Commands sensor to clear calibration data. """
        self.logger.info("Clearing calibration readings")

        # Send take high point calibration command to hardware
        _, error = self.process_command("Cal,clear", processing_seconds=0.3)

        # Check for errors
        if error.exists():
            error.report("Driver unable to clear calibration readings")
            self.logger.error(error.summary())
            return error

        # Successfully cleared calibration readings
        return Error(None)
