# Import standard python modules
from typing import Tuple, Optional 
import time

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error
from device.utilities.health import Health

# Import device drivers
from device.peripherals.modules.atlas_ph.driver import AtlasPHDriver

# Import atlas sensor mixin
from device.peripherals.classes.atlas_sensor import AtlasSensorMixin


class AtlasPHSensor(AtlasSensorMixin):
    """ Atlas pH sensor instance. """

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
        self.driver = AtlasPHDriver(
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

        # Setup successful!
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
               self.sensor_type = "pH"
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
        if self.sensor_type != "pH":
            error = Error("Sensor probe failed, incorrect sensor type. `{}` != `pH`".format(self.sensor_type))
            return error

        # Successfuly probed!
        self.health.reset()
        return Error(None)


    def read_potential_hydrogen(self) -> Tuple[Optional[float], Error]:
        """ Tries to read potential hydrogen until successful or becomes too unhealthy. """

        # Check if simulating
        if self.simulate:
            return 7.4, Error(None)

        # Send commands until success or becomes too healthy
        while self.healthy:

            # Send command
            ec, error = self.driver.read_potential_hydrogen()

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


    def take_mid_point_calibration_reading(self, value: float) -> Error:
        """ Tries to take mid point calibration reading until successful or 
            becomes too unhealthy. """

        # Send commands until success of becomes too healthy
        while self.healthy:

            # Send probe
            error = self.driver.take_mid_point_calibration_reading(value)

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Sensor unable to take mid point calibration reading, became too unhealthy")
            return error

        # Successfuly took mid point calibration reading!
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
