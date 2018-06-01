# Import standard python modules
from typing import Tuple, Optional 
import time

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error
from device.utilities.health import Health

# Import peripheral utilities
from device.peripherals.utilities import light

# Import device drivers
from device.peripherals.modules.atlas_ec.driver import AtlasECDriver


class AtlasECSensor:
    """ Atlas EC sensor instance. """

    def __init__(self, name: str, bus: int, address: str, mux: str = None, 
        channel: int = None, simulate: bool = False) -> None:
        """ Instantiates panel. """

        # Initialize logger
        self.logger = Logger(
            name = "AtlasECSensor({})".format(name),
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


    @property
    def healthy(self):
        return self.health.healthy


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

        if self.driver.firmware_version < 1.95:
            # Successfuly setup older firmware!
            self.logger.warning("Using old circuit stamp (version {}), consider upgrading".format(self.driver.firmware_version))
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
        return Error(None)


    def reset(self):
        """ Resets sensor. """
        self.health.reset()


    def probe(self):
        """ Probes driver until successful or becomes too unhealthy. """

        # Probe until successful or unhealthy
        while self.healthy:

            # Send probe
            error = self.driver.probe()

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Sensor probe failed, became too unhealthy")
            return error

        # Successfuly initialized!
        return Error(None)


    def read_electrical_conductivity(self) -> Tuple[Optional[float], Error]:
        """ Tries to enable protocol lock until successful or becomes too unhealthy. """

        # Check if simulating
        if self.simulate:
            return 2.1, Error(None)

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

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Sensor unable to read electrical conductivity, became too unhealthy")
            return None, error

        # Successfuly read electrical conductivity!
        return ec, Error(None)


    def set_compensation_temperature(self, value: float) -> Error:
        """ Tries to enable protocol lock until successful or becomes too unhealthy. """

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


    def enable_led(self) -> Error:
        """ Tries to enable protocol lock until successful or becomes too unhealthy. """

        # Send commands until success or becomes too healthy
        while self.healthy:

            # Send command
            error = self.driver.enable_led()

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Sensor unable to enable led, became too unhealthy")
            return error

        # Successfuly enabled led!
        return Error(None)


    def set_probe_type(self, value: str) -> Error:
        """ Tries to enable protocol lock until successful or becomes too unhealthy. """

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


    def enable_protocol_lock(self) -> Error:
        """ Tries to enable protocol lock until successful or becomes too unhealthy. """

        # Send commands until success of becomes too healthy
        while self.healthy:

            # Send probe
            error = self.driver.enable_protocol_lock()

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Sensor unable to enable protocol lock, became too unhealthy")
            return error

        # Successfuly enabled protocol lock!
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
