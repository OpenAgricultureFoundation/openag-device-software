# Import standard python modules
from typing import Tuple, Optional
import time

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error
from device.utilities.health import Health

# Import device drivers
from device.peripherals.modules.sht25.driver import SHT25Driver


class SHT25Sensor:
    """SHT25 temperature and humidity sensor."""

    def __init__(
        self,
        name: str,
        bus: int,
        address: str,
        mux: str = None,
        channel: int = None,
        simulate: bool = False,
    ) -> None:

        # Initialize logger
        self.logger = Logger(name="Sensor({})".format(name), dunder_name=__name__)

        # Initialize name and simulation status
        self.name = name
        self.simulate = simulate

        # Initialize driver
        self.driver = SHT25Driver(
            name=name,
            bus=bus,
            address=address,
            mux=mux,
            channel=channel,
            simulate=simulate,
        )

        # Initialize health metrics
        self.health = Health(updates=5, minimum=60)

    @property
    def healthy(self):
        """ Gets sensor healthyness. """
        return self.health.healthy

    def initialize(self) -> Error:
        """ Initializes sensor. """
        self.logger.info("Initializing")

        # Check if simulating
        if self.simulate:
            return Error(None)

        # Probe driver
        error = self.probe()

        # Check for errors:
        if error.exists():
            error.report("Sensor unable to initialize")
            self.logger.error(error.latest())
            return error

        # Successfully initialized!
        self.logger.info("Successfully initialized!")
        return Error(None)

    def setup(self) -> Error:
        """ Sets up sensor. No setup required. """
        self.logger.info("Setting up")
        return Error(None)
        self.logger.info("Successfully setup!")

    def reset(self):
        """ Resets sensor. """
        self.health.reset()

    def probe(self):
        """ Probes driver until successful or becomes too unhealthy. """
        self.logger.info("Probing sensor")

        # Probe until successful or unhealthy
        while self.healthy:

            # Read driver info
            _, error = self.driver.read_user_register()

            # Check if simulating
            if self.simulate:
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

        # Successfuly probed!
        self.health.reset()
        return Error(None)

    def read_temperature(self) -> Tuple[Optional[float], Error]:
        """ Tries to read temperature until successful or becomes too 
            unhealthy. """

        # Check if simulating
        if self.simulate:
            self.logger.info("Simulating reading temperature")
            temperature = 20.2
            self.logger.info("Temperature: {} C".format(temperature))
            return temperature, Error(None)

        # Send commands until success or becomes too healthy
        while self.healthy:

            # Send command
            temperature, error = self.driver.read_temperature()

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
            error.report("Sensor unable to read temperature, became too unhealthy")
            self.logger.error(error.latest())
            return None, error

        # Successfuly read temperature!
        self.health.reset()
        return temperature, Error(None)

    def read_humidity(self) -> Tuple[Optional[float], Error]:
        """ Tries to read humidity until successful or becomes too 
            unhealthy. """

        # Check if simulating
        if self.simulate:
            self.logger.info("Simulating reading humidity")
            humidity = 40.4
            self.logger.info("Humidity: {} %".format(humidity))
            return humidity, Error(None)

        # Send commands until success or becomes too healthy
        while self.healthy:

            # Send command
            humidity, error = self.driver.read_humidity()

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
            error.report("Sensor unable to read humidity, became too unhealthy")
            self.logger.error(error.latest())
            return None, error

        # Successfuly read humidity!
        self.health.reset()
        return humidity, Error(None)
