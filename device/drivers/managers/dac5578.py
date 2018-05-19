# Import standard python modules
from typing import Optional, Tuple

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
                health_minimum: int = 80, health_updates: int = 20) -> None:
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


    def set_output(self, channel: int, percent: int, disable_mux: bool = False) -> Optional[str]:
        """ Sets output value to channel. """
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
