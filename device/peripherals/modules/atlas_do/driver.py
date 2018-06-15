# Import standard python modules
import time
from typing import Optional, Tuple

# Import device comms
from device.comms.i2c import I2C

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error
from device.utilities import math

# Import parent class
from device.peripherals.classes.atlas_driver import AtlasDriver


class AtlasDODriver(AtlasDriver):
    """ Driver for atlas dissolved oxygen sensor. """

    # Initialize sensor properties
    _dissolved_oxygen_accuracy = 0.05 # mg/L
    _min_dissolved_oxygen = 0.01
    _max_dissolved_oxygen = 100


    def __init__(self, name: str, bus: int, address: int, mux: Optional[int] = None, 
                channel: Optional[int] = None, simulate: bool = False) -> None:
        """ Initializes driver. """

        super().__init__(
            name = name, 
            bus = bus, 
            address = address, 
            mux = mux,
            channel = channel,
            logger_name = "Driver({})".format(name), 
            i2c_name = name, 
            dunder_name = __name__, 
            simulate = simulate,
        )


    def read_dissolved_oxygen(self) -> Tuple[float, Error]:
        """ Reads dissolved oxygen from sensor, sets significant 
            figures based off error magnitude, returns value in mg/L. """
        self.logger.debug("Reading dissolved oxygen value from hardware")

        # Get dissolved oxygen reading from hardware
        # Assumed dissolved oxygen is only enabled output
        response, error = self.process_command("R", processing_seconds=0.6)

        # Check for errors
        if error.exists():
            error.report("Unable to read electrical conductivity")
            self.logger.error(error.summary())
            return None, error

        # Parse response
        dissolved_oxygen_raw = float(response)

        # Set significant figures based off error magnitude
        error_magnitude = math.magnitude(self._dissolved_oxygen_accuracy)
        significant_figures = error_magnitude * -1
        dissolved_oxygen = round(dissolved_oxygen_raw, significant_figures)

        # Verify dissolved oxygen value within valid range
        if dissolved_oxygen > self._min_dissolved_oxygen and dissolved_oxygen < self._min_dissolved_oxygen:
            self.logger.warning("Dissolved oxygen outside of valid range")
            dissolved_oxygen = None

        # Successfully read dissolved oxygen!
        self.logger.debug("dissolved_oxygen = {}".format(dissolved_oxygen))
        return dissolved_oxygen, Error(None)


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


    def set_compensation_pressure(self, value: float) -> Error:
        """ Commands sensor to set compensation pressure. """
        self.logger.info("Setting compensation temperature")

        # Send command
        command = "T,{}".format(value)
        _, error = self.process_command(command, processing_seconds=0.3)

        # Check for error
        if error.exists():
            error.report("Driver unable to set compensation pressure")
            self.logger.error(error.summary())
            return error

        # Successfully set compensation pressure!
        return Error(None)


    def set_compensation_electrical_conductivity(self, value_ms_cm: float) -> Error:
        """ Commands sensor to set compensation electrical conductivity. """
        self.logger.info("Setting compensation electrical conductivity")

        # Convert value to uS/Cm
        value_us_cm = value_ms_cm * 1000.0

        # Send command
        command = "S,{}".format(value_us_cm)
        _, error = self.process_command(command, processing_seconds=0.3)

        # Check for error
        if error.exists():
            error.report("Driver unable to set compensation electrical conductivity")
            self.logger.error(error.summary())
            return error

        # Successfully set compensation electrical conductivity!
        return Error(None)


    def enable_mg_l_output(self) -> Error:
        """ Commands sensor to enable dissolved oxygen in mg/L output when 
            reporting readings. """
        self.logger.info("Enabling dissolved oxygen mg/L output in hardware")

        # Send command
        _, error = self.process_command("O,mg,1", processing_seconds=0.3)

        # Check for errors
        if error.exists():
            error.report("Driver unable to enable dissolved oxygen mg/L output")
            self.logger.error(error.summary())
            return error

        # Successfully enabled dissolved oxygen mg/L output!
        return Error(None)


    def disable_mg_l_output(self) -> Error:
        """ Commands sensor to disable dissolved oxygen in mg/L output when 
            reporting readings. """
        self.logger.info("Disabling dissolved oxygen mg/L output in hardware")

        # Send command
        _, error = self.process_command("O,mg,0", processing_seconds=0.3)

        # Check for errors
        if error.exists():
            error.report("Driver unable to disable dissolved oxygen mg/L output")
            self.logger.error(error.summary())
            return error

        # Successfully disabled dissolved oxygen mg/L output!
        return Error(None)


    def enable_percent_saturation_output(self) -> Error:
        """ Commands sensor to enable percent saturation output when 
            reporting readings. """
        self.logger.info("Enabling percent saturation output in hardware")

        # Send command
        _, error = self.process_command("O,%,1", processing_seconds=0.3)
self.logger.error(error.summary())
        # Check for errors
        if error.exists():
            error.report("Driver unable to enable percent saturation output")
            self.logger.error(error.summary())
            return error

        # Successfully enabled percent saturation output!
        return Error(None)


    def disable_percent_saturation_output(self) -> Error:
        """ Commands sensor to disable percent saturation output when 
            reporting readings. """
        self.logger.info("Disabling percent saturation output in hardware")

        # Send command
        _, error = self.process_command("O,%,0", processing_seconds=0.3)

        # Check for errors
        if error.exists():
            error.report("Driver unable to disable percent saturation output")
            self.logger.error(error.summary())
            return error

        # Successfully disabled percent saturation output!
        return Error(None)
