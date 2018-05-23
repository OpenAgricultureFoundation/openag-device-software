# Import standard python modules
import time
from typing import Optional

# Import device utilities
from device.utilities.health import Health
from device.utilities.error import Error

# Import driver parent class
from device.drivers.classes.driver_manager import DriverManager

# Import driver core
from device.drivers.dac5578.core import DAC5578Core


class DAC5578Manager(DriverManager):
    """ Driver manager for DAC5578 digital to analog converter. """

    is_shutdown: bool = False


    def __init__(self, name: str, bus: int, address: int, mux: Optional[int] = None, 
                channel: Optional[int] = None, simulate: bool = False, 
                health_minimum: int = 60, health_updates: int = 5) -> None:
        """ Initializes dac5578 manager. """

        # Instantiate parent class
        super().__init__(
            logger_name = "DAC5578Manager({})".format(name),
            dunder_name = __name__,
            health_minimum = health_minimum,
            health_updates = health_updates,
        )

        # Instantiate core
        self.core = DAC5578Core(
            name = name,
            bus = bus,
            address = address,
            mux = mux,
            channel = channel,
            simulate = simulate,
        )


    def reset(self) -> None:
        """ Reset dac5578. """
        self.logger.debug("Resetting")
        self.core.turn_on()
        self.is_shutdown = False


    def shutdown(self) -> None:
        """ Shutdown dac5578. """
        self.logger.debug("Shutting down")
        self.core.turn_off()


    def set_output(self, channel: int, percent: int, disable_mux: bool = False) -> Error:
        """ Sets output value to channel. Checks channel and percent are valid.
            Returns none on success, error on failure. """
        self.logger.debug("Setting output on channel {} to: {}%".format(channel, percent))

        # Set output
        error = self.core.set_output(channel, percent)

        # Check for errors & update health
        if error.exists():
            error.report("Unable to set output")
            self.logger.error(error)
            self.health.report_failure()
            return error
        else:
            self.logger.debug("Successfully set output")
            self.health.report_success()
            return Error(None)


    def set_outputs(self, outputs: dict) -> Error:
        """ Sets output channels to output percents. Only sets mux once. """
        self.logger.debug("Setting outputs: {}".format(outputs))

        # Set outputs
        error = self.core.set_outputs(outputs)

        # Check for errors & aupdate health
        if error.exists():
            error.report("Unable to set outputs")
            self.logger.error(error)
            self.health.report_failure()
            return error
        else:
            self.logger.debug("Successfully set outputs")
            self.health.report_success()
            return Error(None)


    def probe(self, retry: bool = False, interval_ms: int = 200) -> Error:
        """ Probes health of dac5578. """
        self.logger.debug("Probing dac5578, retry={}, interval_ms={}".format(
            retry, interval_ms))

        # Read power register
        powered, error = self.core.read_power_register()

        # Check for successful probe
        if not error.exists():
            self.logger.debug("Probe successful")
            self.health.report_success()
            return Error(None)

        # Probe failed
        self.logger.debug("Probe failed, error = {}".format(error))
        self.health.report_failure()

        # Check for disabled retry
        if not retry:
            error.report("Probe failed w/out retry")
            self.logger.info("Probe failed w/out retry, shutting down")
            self.shutdown()
            return error
        
        # Retry enabled, check if healthy
        if self.healthy:
            time.sleep(interval_ms)
            self.logger.debug("Retrying at {} ms interval".format(interval_ms))
            self.probe(retry=retry, interval_ms=interval_ms)
        else:
            error.report("Probe failed after retries")
            self.logger.info("Probe failed after retries, shutting down")
            self.shutdown()
            return error
