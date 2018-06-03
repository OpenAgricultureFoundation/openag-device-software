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


class AtlasECDriver(AtlasDriver):
    """ Driver for atlas electrical conductivity sensor. """

    # Initialize sensor properties
    _electrical_conductivity_accuracy_percent = 2


    def __init__(self, name: str, bus: int, address: int, mux: Optional[int] = None, 
                channel: Optional[int] = None, simulate: bool = False) -> None:
        """ Initializes driver. """

        super().__init__(
            name = name, 
            bus = bus, 
            address = address, 
            mux = mux,
            channel = channel,
            logger_name = "AtlasECDriver-{}".format(name), 
            i2c_name = "AtlasEC-{}".format(name), 
            dunder_name = __name__, 
            simulate = simulate,
        )


    def read_electrical_conductivity(self) -> Tuple[float, Error]:
        """ Reads electrical conductivity from sensor, sets significant 
            figures based off error magnitude, returns value in mS/cm. """
        self.logger.info("Reading electrical conductivity value from hardware")

        # Get electrical conductivity reading from hardware
        # Assumes electrical conductivity is only enabled output
        response, error = self.process_command("R", processing_seconds=0.6)

        # Check for errors
        if error.exists():
            error.report("Driver unable to read electrical conductivity")
            return None, error

        # Parse response
        electrical_conductivity_us_cm = float(response)

        # Convert from uS/cm to mS/cm
        electrical_conductivity = electrical_conductivity_us_cm / 1000

        # Set significant figures based off error magnitude
        error_value = electrical_conductivity * self._electrical_conductivity_accuracy_percent / 100
        error_magnitude = math.magnitude(error_value)
        significant_figures = error_magnitude * -1
        electrical_conductivity = round(electrical_conductivity, significant_figures) # TODO: Does this work well on a BBB?

        # Successfully read electical conductivity!
        self.logger.debug("electrical_conductivity = {}".format(electrical_conductivity))
        return electrical_conductivity, Error(None)


    def set_compensation_temperature(self, temperature: float) -> Error:
        """ Commands sensor to set compensation temperature. """
        self.logger.info("Setting compensation temperature")

        # Send command
        command = "T,{}".format(temperature)
        _, error = self.process_command(command, processing_seconds=0.3)

        # Check for error
        if error.exists():
            error.report("Driver unable to set compensation temperature")
            return error

        # Successfully set compensation temperature!
        return Error(None)


    def enable_electrical_conductivity_output(self) -> Error:
        """ Commands sensor to enable electrical conductivity output when 
            reporting readings. """
        self.logger.info("Enabling electrical conductivity output in hardware")

        # Send command
        _, error = self.process_command("O,EC,1", processing_seconds=0.3)

        # Check for errors
        if error.exists():
            error.report("Driver unable to enable electrical conductivity output")
            return error

        # Successfully enabled electrical conductivity output!
        return Error(None)


    def disable_electrical_conductivity_output(self) -> Error:
        """ Commands sensor to disable electrical conductivity output when 
            reporting readings. """
        self.logger.info("Disabling electrical conductivity output in hardware")

        # Send command
        _, error = self.process_command("O,EC,0", processing_seconds=0.3)

        # Check for errors
        if error.exists():
            error.report("Driver unable to disable electrical conductivity output")
            return error

        # Successfully disabled electrical conductivity output!
        return Error(None)


    def enable_total_dissolved_solids_output(self) -> Error:
        """ Commands sensor to enable total dissolved solids output when 
            reporting readings. """
        self.logger.info("Enabling total dissolved solids output in hardware")

        # Send command
        _, error = self.process_command("O,TDS,1", processing_seconds=0.3)

        # Check for errors
        if error.exists():
            error.report("Driver unable to enable total dissolved solids output")
            return error

        # Successfully enabled total dissolved solids output!
        return Error(None)


    def disable_total_dissolved_solids_output(self) -> Error:
        """ Commands sensor to disable total dissolved solids output when 
            reporting readings. """
        self.logger.info("Disabling total dissolved solids output in hardware")

        # Send command
        _, error = self.process_command("O,TDS,0", processing_seconds=0.3)

        # Check for errors
        if error.exists():
            error.report("Driver unable to disable total dissolved solids output")
            return error

        # Successfully disabled total dissolved solids output!
        return Error(None)


    def enable_salinity_output(self) -> Error:
        """ Commands sensor to enable salinity output when reporting 
            readings. """
        self.logger.info("Enabling salinity output in hardware")

        # Send command
        _, error = self.process_command("O,S,1", processing_seconds=0.3)

        # Check for errors
        if error.exists():
            error.report("Driver unable to enable salinity output")
            return error

        # Successfully enabled salinity output!
        return Error(None)


    def disable_salinity_output(self) -> Error:
        """ Commands sensor to disable salinity output when reporting 
            readings. """
        self.logger.info("Disabling salinity output in hardware")

        # Send command
        _, error = self.process_command("O,S,0", processing_seconds=0.3)

        # Check for errors
        if error.exists():
            error.report("Driver unable to disable salinity output")
            return error

        # Successfully disabled salinity output!
        return Error(None)


    def enable_specific_gravity_output(self) -> Error:
        """ Commands sensor to enable specific gravity output when reporting
            readings. """
        self.logger.info("Enabling specific gravity output in hardware")

        # Send command
        _, error = self.process_command("O,SG,1", processing_seconds=0.3)

        # Check for errors
        if error.exists():
            error.report("Driver unable to enable specific gravity output")
            return error

        # Successfully enabled specific gravity output!
        return Error(None)


    def disable_specific_gravity_output(self) -> Error:
        """ Commands sensor to disable specific gravity output when reporting
            readings. """
        self.logger.info("Disabling specific gravity output in hardware")

        # Send command
        _, error = self.process_command("O,SG,0", processing_seconds=0.3)

        # Check for errors
        if error.exists():
            error.report("Driver unable to disable specific gravity output")
            return error

        # Successfully disable specific gravity output!
        return Error(None)


    def set_probe_type(self, value: str) -> Error:
        """ Commands sensor to set probe type to value. """
        self.logger.info("Setting probe type in hardware")

        # Send command
        _, error = self.process_command("K,{}".format(value), processing_seconds=0.3)

        # Check for errors
        if error.exists():
            error.report("Driver unable to set probe type")
            return error

        # Successfully set probe type!
        return Error(None)


    def take_dry_calibration_reading(self) -> Error:
        """ Commands sensor to take a dry calibration reading. """
        self.logger.info("Taking dry calibration reading in hardware")

        # Send command
        _, error = self.process_command("Cal,dry", processing_seconds=0.6)

        # Check for errors
        if error.exists():
            error.report("Driver unable to take dry calibration reading")
            return error

        # Successfully took dry calibration reading!
        return Error(None)


    def take_single_point_calibration_reading(self, electrical_conductivity: float) -> Error:
        """ Commands sensor to take a single point calibration reading. """
        self.logger.info("Taking single point calibration reading in hardware.")

        # Convert mS/cm to uS/cm
        electrical_conductivity_us_cm = electrical_conductivity * 1000

        # Send command
        command = "Cal,{}".format(electrical_conductivity_us_cm)
        _, error = self.process_command(command, processing_seconds=0.6)

        # Check for errors-> Error
        if error.exists():
            error.report("Driver unable to take single point calibration reading")
            return error

        # Successfully took single point calibration reading!
        return Error(None)


    def take_low_point_calibration_reading(self, electrical_conductivity: float) -> Error:
        """ Commands sensor to take a low point calibration reading. """
        self.logger.info("Taking low point calibration reading in hardware.")

        # Convert mS/cm to uS/cm
        electrical_conductivity_us_cm = electrical_conductivity * 1000

        # Send command
        command = "Cal,low,{}".format(electrical_conductivity_us_cm)
        _, error = self.process_command(command, processing_seconds=0.6)

        # Check for errors
        if error.exists():
            error.report("Driver unable to take low point calibration reading")
            return error

        # Successfully took low point calibration reading!
        return Error(None)


    def take_high_point_calibration_reading(self, electrical_conductivity: float) -> Error:
        """ Commands sensor to take a high point calibration reading. """
        self.logger.info("Taking high point calibration reading in hardware.")

        # Convert mS/cm to uS/cm
        electrical_conductivity_us_cm = electrical_conductivity * 1000

        # Send command
        command = "Cal,high,{}".format(electrical_conductivity_us_cm)
        _, error = self.process_command(command, processing_seconds=0.6)

        # Check for errors
        if error.exists():
            error.report("Driver unable to take high point calibration reading")
            return error

        # Successfully took high point calibration reading!
        return Error(None)


    def clear_calibration_readings(self) -> Error:
        """ Commands sensor to clear calibration readings. """
        self.logger.info("Clearing calibration readings.")

        # Send command
        _, error = self.process_command("Cal,clear", processing_seconds=0.3)

        # Check for errors
        if error.exists():
            error.report("Driver unable to clear calibration readings")
            return error

        # Successfully cleared calibration readings!
        return Error(None)
