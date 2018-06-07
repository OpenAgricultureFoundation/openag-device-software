# Import standard python modules
from typing import Tuple, Optional 
import time

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error
from device.utilities.health import Health

# Import device drivers
from device.peripherals.modules.atlas_ec.driver import AtlasECDriver

# Import atlas sensor mixin
from device.peripherals.classes.atlas_sensor import AtlasSensorMixin


class AtlasECSensor(AtlasSensorMixin):
    """ Atlas EC sensor instance. """

    def __init__(self, name: str, bus: int, address: str, mux: str = None, 
        channel: int = None, simulate: bool = False) -> None:
        """ Instantiates panel. """

        # Initialize logger
        self.logger = Logger(
            name = "Sensor({})".format(name),
            dunder_name = __name__,
        )
        
        # Initialize name and simulation status
        self.name = name
        self.simulate = simulate

        # Initialize driver
        self.driver = AtlasECDriver(
            name = name,
            bus = bus,
            address = address,
            mux = mux,
            channel = channel,
            simulate = simulate,
        )

        # Initialize health metrics
        self.health = Health(updates = 5, minimum = 60)


    def initialize(self) -> Error:
        """ Initializes sensor. """

        # Check if simulating
        if self.simulate:
            return Error(None)
        
        # Probe driver
        error = self.probe()

        # Check for errors:
        if error.exists():
            error.report("Sensor unable to initialize")
            return error

        # Successfully initialized!
        return Error(None)


    def setup(self) -> Error:
        """ Sets up sensor. """

        # Check if simulating
        if self.simulate:
            return Error(None)

        # Enable led
        error = self.enable_led()

        # Check for errors:
        if error.exists():
            error.report("Sensor setup failed")
            return error

        # Set probe type
        error = self.set_probe_type("1.0")

        # Check for errors:
        if error.exists():
            error.report("Sensor setup failed")
            return error

        # Check if using new firmware
        if self.firmware_version < 1.95:
            # Successfuly setup older firmware!
            self.logger.warning("Using old circuit stamp (version {}), consider upgrading".format(self.firmware_version))
            return Error(None)

        # Enable protocol lock
        error = self.enable_protocol_lock()

        # Check for errors:
        if error.exists():
            error.report("Sensor setup failed")
            return error

        # Enable electrical conductivity output
        error = self.enable_electrical_conductivity_output()

        # Check for errors:
        if error.exists():
            error.report("Sensor setup failed")
            return error

        # Disable total dissolved solids output
        error = self.disable_total_dissolved_solids_output()

        # Check for errors:
        if error.exists():
            error.report("Sensor setup failed")
            return error

        # Disable salinity output
        error = self.disable_salinity_output()

        # Check for errors:
        if error.exists():
            error.report("Sensor setup failed")
            return error

        # Disable specific gravity output
        error = self.disable_specific_gravity_output()

        # Check for errors:
        if error.exists():
            error.report("Sensor setup failed")
            return error

        # Setup successful!
        self.health.reset()
        return Error(None)


    def reset(self):
        """ Resets sensor. """
        self.health.reset()


    def probe(self):
        """ Probes driver until successful or becomes too unhealthy. """

        # Probe until successful or unhealthy
        while self.healthy:

            # Read driver info
            self.sensor_type, self.firmware_version, error = self.driver.read_info()

           # Check if simulating
            if self.simulate:
               self.sensor_type = "EC"
               self.firmware_version = 2.0
               error = Error(None)
               break

           # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

            # Retry every few seconds
            time.sleep(3)

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Sensor probe failed, became too unhealthy")
            return error

        # Check for correct sensor type
        if self.sensor_type != "EC":
            error = Error("Sensor probe failed, incorrect sensor type. `{}` != `EC`".format(self.sensor_type))
            return error

        # Successfuly probed!
        self.health.reset()
        return Error(None)


    def read_electrical_conductivity(self) -> Tuple[Optional[float], Error]:
        """ Tries to read electrical conductivity until successful or becomes too unhealthy. """
        self.logger.debug("Reading electrical conductivity")

        # Check if simulating
        if self.simulate:
            ec = 2.1
            self.logger.info("EC: {} mS/cm".format(ec))
            return ec, Error(None)

        # Send commands until success or becomes too healthy
        while self.healthy:

            # Send command
            ec, error = self.driver.read_electrical_conductivity()

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

            # Retry every few seconds
            time.sleep(3)

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Sensor unable to read electrical conductivity, became too unhealthy")
            return None, error

        # Successfuly read electrical conductivity!
        self.health.reset()
        return ec, Error(None)


    def set_compensation_temperature(self, value: float) -> Error:
        """ Tries to set compensation temperature until successful or becomes too unhealthy. """

        # Send commands until success or becomes too healthy
        while self.healthy:

            # Send command
            error = self.driver.set_compensation_temperature(value)

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Sensor unable to set compensation temperature, became too unhealthy")
            return error

        # Successfuly set compensation temperature!
        return Error(None)


    def set_probe_type(self, value: str) -> Error:
        """ Tries to set probe type until successful or becomes too unhealthy. """
        self.logger.info("Setting probe type: `{}`".format(value))

        # Send commands until success of becomes too healthy
        while self.healthy:

            # Send probe
            error = self.driver.set_probe_type(value)

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Sensor unable to set probe type, became too unhealthy")
            return error

        # Successfuly set probe type!
        return Error(None)


    def enable_electrical_conductivity_output(self) -> Error:
        """ Tries to enable electrical conductivity output until successful or 
            becomes too unhealthy. """

        # Send commands until success of becomes too healthy
        while self.healthy:

            # Send probe
            error = self.driver.enable_electrical_conductivity_output()

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Sensor unable to enable electrical conductivity output, became too unhealthy")
            return error

        # Successfuly enabled electrical conductivity output!
        return Error(None)


    def disable_total_dissolved_solids_output(self) -> Error:
        """ Tries to disable electrical conductivity output until successful or 
            becomes too unhealthy. """

        # Send commands until success of becomes too healthy
        while self.healthy:

            # Send probe
            error = self.driver.disable_total_dissolved_solids_output()

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Sensor unable to disable total dissolved solids output, became too unhealthy")
            return error

        # Successfuly disabled total dissolved solids output!
        return Error(None)


    def disable_salinity_output(self) -> Error:
        """ Tries to disable salinity output until successful or 
            becomes too unhealthy. """

        # Send commands until success of becomes too healthy
        while self.healthy:

            # Send probe
            error = self.driver.disable_salinity_output()

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Sensor unable to disable salinity output, became too unhealthy")
            return error

        # Successfuly disabled salinity output!
        return Error(None)


    def disable_specific_gravity_output(self) -> Error:
        """ Tries to disable specific gravity output until successful or 
            becomes too unhealthy. """

        # Send commands until success of becomes too healthy
        while self.healthy:

            # Send probe
            error = self.driver.disable_specific_gravity_output()

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Sensor unable to disable specific gravity output, became too unhealthy")
            return error

        # Successfuly disabled specific gravity output!
        return Error(None)



    def take_dry_calibration_reading(self) -> Error:
        """ Tries to take dry calibration reading until successful or 
            becomes too unhealthy. """

        # Send commands until success of becomes too healthy
        while self.healthy:

            # Send probe
            error = self.driver.take_dry_calibration_reading()

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Sensor unable to take dry calibration reading, became too unhealthy")
            return error

        # Successfuly took dry calibration reading!
        return Error(None)


    def take_single_point_calibration_reading(self, value: float) -> Error:
        """ Tries to take single point calibration reading until successful or 
            becomes too unhealthy. """

        # Send commands until success of becomes too healthy
        while self.healthy:

            # Send probe
            error = self.driver.take_single_point_calibration_reading(value)

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Sensor unable to take single point calibration reading, became too unhealthy")
            return error

        # Successfuly took single point calibration reading!
        return Error(None)


    def take_low_point_calibration_reading(self, value: float) -> Error:
        """ Tries to take low point calibration reading until successful or 
            becomes too unhealthy. """

        # Send commands until success of becomes too healthy
        while self.healthy:

            # Send probe
            error = self.driver.take_low_point_calibration_reading(value)

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Sensor unable to take low point calibration reading, became too unhealthy")
            return error

        # Successfuly took low point calibration reading!
        return Error(None)


    def take_high_point_calibration_reading(self, value: float) -> Error:
        """ Tries to take high point calibration reading until successful or 
            becomes too unhealthy. """

        # Send commands until success of becomes too healthy
        while self.healthy:

            # Send probe
            error = self.driver.take_high_point_calibration_reading(value)

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Sensor unable to take high point calibration reading, became too unhealthy")
            return error

        # Successfuly took high point calibration reading!
        return Error(None)


    def clear_calibration_readings(self) -> Error:
        """ Tries to clear calibration readings until successful or 
            becomes too unhealthy. """

        # Send commands until success of becomes too healthy
        while self.healthy:

            # Send probe
            error = self.driver.clear_calibration_readings()

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Sensor unable to clear calibration readings, became too unhealthy")
            return error

        # Successfuly cleared calibration readings!
        return Error(None)
