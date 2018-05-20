# Import standard python modules
from typing import Optional

# Import device utilities
from device.utilities.health import Health

# Import driver parent class
from device.drivers.classes.driver_manager import DriverManager

# Import driver core
from device.drivers.cores.dac5578 import DAC5578Core


class DAC5578Manager(DriverManager):
    """ Driver manager for DAC5578 digital to analog converter. """

    def __init__(self, name: str, bus: int, address: int, mux: Optional[int] = None, 
                channel: Optional[int] = None, simulate: bool = False, 
                health_minimum: int = 60, health_updates: int = 5) -> None:
        """ Initializes I2C driver. """

        # Initialize parent class
        super().__init__(
            logger_name = "DAC5578Manager({})".format(name),
            dunder_name = __name__,
            health_minimum = health_minimum,
            health_updates = health_updates,
        )

        # Initialize core
        self.core = DAC5578Core(
            name = name,
            bus = bus,
            address = address,
            mux = mux,
            channel = channel,
            simulate = simulate,
        )


    def probe(self, retry: bool = False, interval_ms: int = 200) -> Optional[str]:
        """ Probes health of dac5578. """
        self.logger.debug("Probing dac5578, retry={}, interval_ms={}".format(
            until_failure, retry_interval_ms))

        # Read power register
        error, powered = self.core.read_power_register()

        # Check for successful probe
        if self.error == None:
            self.logger.debug("Probe successful")
            self.health.report_success()
            return None

        # Probe failed
        self.logger.debug("Probe failed, error = {}".format(error))
        self.health.report_failure()

        # Check for disabled retry
        if not retry:
            self.logger.info("Probe failed w/out retry, shutting down")
            self.shutdown()
            return error
        
        # Retry enabled, check if healthy
        if self.healthy:
            time.sleep(interval_ms)
            self.logger.debug("Retrying at {} ms interval".format(interval_ms))
            self.probe(retry=retry, interval_ms=interval_ms)
        else:
            self.logger.info("Probe failed w/retry, shutting down")
            self.shutdown()
            return ""








        # Fastest method to determine if device is alive
        # Optional retry until failure?
        # Optional retry rate?

        # Let this be called even if driver is shutdown, it is how
        # we will know device is back online
        
        # How should we probe device on startup? - until failure with a low 
        # retry rate --> 2 seconds?

        # Note: only log warning
        ...


    def reset(self) -> None:
        """ Reset dac5578. """
        self.logger.debug("Resetting")
        self.core.turn_on()
        self.shutdown = False


    def shutdown(self) -> None:
        """ Shutdown dac5578. """
        self.logger.debug("Shutting down")
        self.core.turn_off()


    @property
    def shutdown(self) -> bool:
        """ Get shutdown status. """
        try:
            return self._shutdown
        except NameError:
            self._shutdown = False
            return self._shutdown


    @shutdown.setter
    def shutdown(self, value: bool) -> None:
        """ Set shutdown status. """
        self._shutdown = value


    def set_output(self, channel: int, percent: int, disable_mux: bool = False) -> Optional[str]:
        """ Sets output value to channel. Checks channel and percent are valid.
            Returns none on success, error on failure. """
        self.logger.debug("Setting output on channel {} to: {}%".format(channel, percent))

        # Check valid channel range
        if channel < 0 or channel > 7:
            return "Channel out of range, must be within 0-7"

        # Check valid value range
        if percent < 0 or percent > 100:
            return "Output percent out of range, must be within 0-100"

        # Set output
        error = self.core.set_output(channel, percent)

        # Check for errors & update health
        if error != None:
            self.logger.error("Unable to set output")
            self.health.report_failure()
            return error
        else:
            self.logger.debug("Successfully set output")
            self.health.report_success()
            return None


    def set_outputs(self, outputs: dict) -> Optional[str]:
        """ Sets output channels to output percents. Only sets mux once. """
        self.logger.debug("Setting outputs: {}".format(outputs))

        # Validate outputs
        for channel, percent in outputs.items():

            # Check valid channel range
            if channel < 0 or channel > 7:
                return "Channel out of range, must be within 0-7"

            # Check valid value range
            if percent < 0 or percent > 100:
                return "Output percent out of range, must be within 0-100"

        # Set outputs
        error = self.core.set_outputs(outputs)

        # Check for errors & aupdate health
        if error != None:
            self.logger.error("Unable to set outputs")
            self.health.report_failure()
            return error
        else:
            self.logger.debug("Successfully set outputs")
            self.health.report_success()
            return None
