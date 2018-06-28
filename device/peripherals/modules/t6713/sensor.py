# Import standard python modules
from typing import Tuple, Optional
import time

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error
from device.utilities.health import Health

# Import device drivers
from device.peripherals.modules.t6713.driver import T6713Driver, Status


class T6713Sensor:
    """ T6713 carbon dioxide sensor. """

    # Initialize warmup parameters
    _warmup_timeout = 120  # seconds

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
        self.logger = Logger(name="Sensor({})".format(name), dunder_name=__name__)

        # Initialize name and simulation status
        self.name = name
        self.simulate = simulate

        # Initialize driver
        self.driver = T6713Driver(
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

    def setup(self) -> Error:
        """ Sets up sensor. """
        self.logger.info("Setting up")

        # Check if simulating
        if self.simulate:
            return Error(None)

        # Disable abc logic
        error = self.disable_abc_logic()

        # Check for errors:
        if error.exists():
            error.report("Sensor setup failed")
            self.logger.error(error.latest())
            return error

        # Wait at least 2 minutes for sensor to stabilize
        if not self.simulate:
            start_time = time.time()
            while time.time() - start_time < 120:

                # Keep logs active
                self.logger.info("Warming up, waiting for 2 minutes")

                # Update every few seconds
                time.sleep(3)

        # Wait for sensor to report exiting warm up mode
        start_time = time.time()
        while True:

            # Keep logs active
            self.logger.info("Warming up, waiting for status")

            # Send read status command
            status, error = self.read_status()

            # Check for errors
            if error.exists():
                error.report("Sensor setup failed")
                self.logger.error(error.latest())
                return error

            # Check if sensor completed warm up mode
            if not status.warm_up_mode:
                self.logger.info("Warmup complete")
                break

            # Check if timed out
            if time.time() - start_time > self._warmup_timeout:
                error = Error("Warmup timed out")
                self.logger.error(error.latest())
                return error

            # Update every 3 seconds
            time.sleep(3)

        # Setup successful!
        self.logger.info("Setup successful")
        self.health.reset()
        return Error(None)

    def reset(self):
        """ Resets sensor. """
        self.logger.info("Resetting")
        self.health.reset()

    def probe(self):
        """ Probes driver until successful or becomes too unhealthy. """
        self.logger.info("Probing")

        # Probe until successful or unhealthy
        while self.healthy:

            # Read driver status
            status, error = self.driver.read_status()

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

        # Check if sensor has error status
        if status.error_condition:
            error.report("Sensor probe failed, error condition in status")
            self.logger.error(error.latest())
            return error

        # Successfuly probed!
        self.health.reset()
        return Error(None)

    def read_carbon_dioxide(self) -> Tuple[Optional[float], Error]:
        """ Tries to read carbon dioxide until successful or becomes too 
            unhealthy. """

        # Check if simulating
        if self.simulate:
            self.logger.info("Simulating reading Co2")
            co2 = 430
            self.logger.info("Co2: {} ppm".format(co2))
            return co2, Error(None)

        # Send commands until success or becomes too healthy
        while self.healthy:

            # Send command
            carbon_dioxide, error = self.driver.read_carbon_dioxide()

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
            error = Error("Sensor unable to read carbon dioxide, became too unhealthy")
            self.logger.error(error.latest())
            return None, error

        # Successfuly read carbon dioxide!
        self.health.reset()
        return carbon_dioxide, Error(None)

    def read_status(self) -> Tuple[Optional[Status], Error]:
        """ Tries to read status until successful or becomes too 
            unhealthy. """

        # Send commands until success or becomes too healthy
        while self.healthy:

            # Send command
            status, error = self.driver.read_status()

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Sensor unable to read status, became too unhealthy")
            self.logger.error(error.latest())
            return None, error

        # Successfuly read status!
        self.health.reset()
        return status, Error(None)

    def enable_abc_logic(self) -> Error:
        """ Tries to disable abc logic until successful or becomes too 
            unhealthy. """

        # Send commands until success or becomes too healthy
        while self.healthy:

            # Send command
            error = self.driver.enable_abc_logic()

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Sensor unable to enable abc logic, became too unhealthy")
            self.logger.error(error.latest())
            return None, error

        # Successfuly enabled abc logic!
        return Error(None)

    def disable_abc_logic(self) -> Error:
        """ Tries to disable abc logic until successful or becomes too 
            unhealthy. """

        # Send commands until success or becomes too healthy
        while self.healthy:

            # Send command
            error = self.driver.disable_abc_logic()

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Sensor unable to disable abc logic, became too unhealthy")
            self.logger.error(error.latest())
            return None, error

        # Successfuly disabled abc logic!
        return Error(None)
