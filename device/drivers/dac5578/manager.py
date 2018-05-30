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
        self.is_shutdown = False


    def shutdown(self) -> None:
        """ Shutdown dac5578. """
        self.logger.debug("Shutting down")
        self.is_shutdown = True


    def set_output(self, channel: int, percent: int, disable_mux: bool = False) -> Error:
        """ Sets output value to channel. Checks channel and percent are valid.
            Returns none on success, error on failure. """
        self.logger.debug("Setting output on channel {} to: {}%".format(channel, percent))

        # Verify dac is not shutdown
        if self.is_shutdown:
            return Error("Unable to set output, dac is shutdown")

        # Verify dac is healthy
        if not self.health.healthy:
            return Error("Unable to set output, dac is unhealthy")

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

        # Verify dac is not shutdown
        if self.is_shutdown:
            return Error("Unable to set outputs, dac is shutdown")

        # Verify dac is healthy
        if not self.health.healthy:
            return Error("Unable to set outputs, dac is unhealthy")

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
        self.logger.debug("Probing, retry={}, interval_ms={}".format(
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


    def turn_on(self, channel: Optional[int] = None) -> Error:
        """ Turns on all channels if no channel is specified. """

        # Set channel or channels
        if channel != None:
            self.logger.debug("Turning on channel {}".format(channel))
            error = self.set_output(channel, 100)
        else:
            self.logger.debug("Turning on all channels")
            outputs = {0: 100, 1: 100, 2: 100, 3: 100, 4: 100, 5: 100, 6: 100, 7: 100}
            error = self.set_outputs(outputs)

        # Check for errors
        if error.exists():
            error.report("Manager unable to turn on")
            return error
        else:
            return Error(None)


    def turn_off(self, channel: Optional[int] = None) -> Error:
        """ Turns on all channels if no channel is specified. """

        # Set channel or channels
        if channel != None:
            self.logger.debug("Turning off channel {}".format(channel))
            error = self.set_output(channel, 0)
        else:
            self.logger.debug("Turning off all channels")
            outputs = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
            error = self.set_outputs(outputs)

        # Check for errors
        if error.exists():
            error.report("Manager unable to turn off")
            return error
        else:
            return Error(None)


    def fade(self, cycles: int, channel: Optional[int] = None) -> Error:
        """ Fades through all channels if no channel is specified. """
        self.logger.debug("Fading {channel}".format(channel = "all channels" if \
            channel == None else "channel: " + str(channel)))

        # Turn off channels
        self.turn_off()

        # Check for errors
        if error.exists():
            error.report("Panel unable to fade")
            return error

        # Set channel or channels
        if channel != None:
            minimum = channel
            maximum = channel + 1
        else:
            minimum = 0
            maximum = 8

        # Repeat for number of specified cycles
        for i in range(cycles):

            # Cycle through channels
            for channel in range(minimum, maximum):

                # Fade up
                for value in range(0, 100, 10):
                    self.logger.info("Channel {}: {}%".format(channel, value))
                    outputs[channel] = value
                    error = self.set_output(channel, value)
                    if error.exists():
                        self.logger.warning("Error: {}".format(error.trace))
                        return error
                    time.sleep(0.1)

                # Fade down
                for value in range(100, 0, -10):
                    self.logger.info("Channel {}: {}%".format(channel, value))
                    outputs[channel] = value
                    error = self.set_output(channel, value)
                    if error.exists():
                        self.logger.warning("Error: {}".format(error.trace))
                        return error
                    time.sleep(0.1)

        return Error(None)