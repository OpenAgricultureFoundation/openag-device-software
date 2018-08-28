# Import standard python modules
from typing import Tuple, Optional
import time

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error
from device.utilities.health import Health

# Import device drivers
from device.peripherals.modules.atlas_do.driver import AtlasDODriver

# Import atlas sensor mixin
from device.peripherals.classes.atlas_sensor import AtlasSensorMixin


class AtlasDOSensor(AtlasSensorMixin):
    """ Atlas EC sensor instance. """

    def __init__(
        self,
        name: str,
        bus: int,
        address: str,
        mux: str = None,
        channel: int = None,
        simulate: bool = False,
    ) -> None:
        """ Instantiates panel. """

        # Initialize logger
        self.logger = Logger(
            name="AtlasDOSensor({})".format(name), dunder_name=__name__
        )

        # Initialize name and simulation status
        self.name = name
        self.simulate = simulate

        # Initialize driver
        self.driver = AtlasDODriver(
            name=name,
            bus=bus,
            address=address,
            mux=mux,
            channel=channel,
            simulate=simulate,
        )

        # Initialize health metrics
        self.health = Health(updates=5, minimum=60)

    # def initialize(self) -> Error:
    #     """ Initializes sensor. """

    #     # Check if simulating
    #     if self.simulate:
    #         return Error(None)

    #     # Probe driver
    #     error = self.probe()

    #     # Check for errors:
    #     if error.exists():
    #         error.report("Sensor unable to initialize")
    #         return error

    #     # Successfully initialized!
    #     return Error(None)

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
            self.logger.error(error.latest())
            return error

        # Check if using new firmware
        if self.firmware_version < 1.95:
            # Successfuly setup older firmware!
            self.logger.warning(
                "Using old circuit stamp (version {}), consider upgrading".format(
                    self.firmware_version
                )
            )
            return Error(None)

        # Enable protocol lock
        error = self.enable_protocol_lock()

        # Check for errors:
        if error.exists():
            error.report("Sensor setup failed")
            self.logger.error(error.latest())
            return error

        # Enable dissolved oxygen in mg/L output
        error = self.enable_mg_l_output()

        # Check for errors:
        if error.exists():
            error.report("Sensor setup failed")
            self.logger.error(error.latest())
            return error

        # Disable percent saturation output
        error = self.disable_percent_saturation_output()

        # Check for errors:
        if error.exists():
            error.report("Sensor setup failed")
            self.logger.error(error.latest())
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
                self.sensor_type = "DO"
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
            self.logger.error(error.latest())
            return error

        # Check for correct sensor type
        if self.sensor_type != "DO":
            error = Error(
                "Sensor probe failed, incorrect sensor type. `{}` != `DO`".format(
                    self.sensor_type
                )
            )
            self.logger.error(error.latest())
            return error

        # Successfuly probed!
        self.health.reset()
        return Error(None)

    def read_dissolved_oxygen(self) -> Tuple[Optional[float], Error]:
        """ Tries to read dissolved oxygen until successful or becomes too unhealthy. """

        # Check if simulating
        if self.simulate:
            return 10.2, Error(None)

        # Send commands until success or becomes too healthy
        while self.healthy:

            # Send command
            do, error = self.driver.read_dissolved_oxygen()

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
            error.report("Sensor unable to read dissolved oxygen, became too unhealthy")
            self.logger.error(error.latest())
            return None, error

        # Successfuly read dissolved oxygen!
        self.health.reset()
        return do, Error(None)

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
            error.report(
                "Sensor unable to set compensation temperature, became too unhealthy"
            )
            self.logger.error(error.latest())
            return error

        # Successfuly set compensation temperature!
        return Error(None)

    def set_compensation_pressure(self, value: float) -> Error:
        """ Tries to set compensation pressure until successful or becomes too unhealthy. """

        # Send commands until success or becomes too healthy
        while self.healthy:

            # Send command
            error = self.driver.set_compensation_pressure(value)

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report(
                "Sensor unable to set compensation pressure, became too unhealthy"
            )
            self.logger.error(error.latest())
            return error

        # Successfuly set compensation pressure!
        return Error(None)

    def set_compensation_electrical_conductivity(self, value: float) -> Error:
        """ Tries to set compensation electrical conductivity until successful or becomes too unhealthy. """

        # Send commands until success or becomes too healthy
        while self.healthy:

            # Send command
            error = self.driver.set_compensation_electrical_conductivity(value)

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report(
                "Sensor unable to set compensation electrical conductivity, became too unhealthy"
            )
            self.logger.error(error.latest())
            return error

        # Successfuly set compensation electrical conductivity!
        return Error(None)

    def enable_mg_l_output(self) -> Error:
        """ Tries to enable dissolved oxygen mg/L output until successful or 
            becomes too unhealthy. """

        # Send commands until success of becomes too healthy
        while self.healthy:

            # Send probe
            error = self.driver.enable_mg_l_output()

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Sensor unable to enable mg/L output, became too unhealthy")
            self.logger.error(error.latest())
            return error

        # Successfuly enabled mg/L output!
        return Error(None)

    def disable_percent_saturation_output(self) -> Error:
        """ Tries to disable percent saturation output until successful or 
            becomes too unhealthy. """

        # Send commands until success of becomes too healthy
        while self.healthy:

            # Send probe
            error = self.driver.disable_percent_saturation_output()

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report(
                "Sensor unable to disable percent saturation output, became too unhealthy"
            )
            self.logger.error(error.latest())
            return error

        # Successfuly disabled percent saturation output!
        return Error(None)
