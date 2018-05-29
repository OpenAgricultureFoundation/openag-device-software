# Import standard python modules
from typing import Tuple, Optional 

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error

# Import peripheral utilities
from device.peripherals.utilities import light

# Import device drivers
from device.drivers.dac5578.manager import DAC5578Manager as DAC5578


class LEDPanel:
    """ An led panel controlled by a dac5578. """

    # Initialize shutdown state
    is_shutdown: bool = False


    def __init__(self, name, channel_configs, bus, address, mux=None, channel=None, simulate=False):
        """ Instantiates panel. """

        # Instantiate logger
        self.logger = Logger(
            name = "LEDPanel({})".format(name),
            dunder_name = __name__,
        )
        
        # Initialize name and channel configs
        self.name = name
        self.channel_configs = channel_configs

        # Instantiate driver
        self.dac5578 = DAC5578(
            name = name,
            bus = bus,
            address = address,
            mux = mux,
            channel = channel,
            simulate = simulate,
        )

        # Initialize health
        self.health = self.dac5578.health
 

    def initialize(self) -> Error:
        """ Initializes panel by probing driver with retry enabled. """
        self.logger.debug("Initializing panel")

        # Probe dac
        error = self.dac5578.probe(retry=True)

        # Check for errors
        if error.exists():
            error.report("Panel initialization failed")
            self.logger.warning(error)
            return error
        
        # Success!
        self.logger.debug("Successfully initialized")
        return Error(None)


    def shutdown(self):
        """ Shutdown panel. """
        self.logger.debug("Shutting down")
        self.dac5578.shutdown()
        self.is_shutdown = True


    def reset(self):
        """ Resets panel. """
        self.logger.debug("Resetting")
        self.dac5578.reset()
        self.is_shutdown = False


    def set_output(self, channel_name: str, percent: float) -> Error:
        """ Sets output on dac. Converts channel name to channel number 
            then sets output on dac. """
        self.logger.debug("Setting output on channel {} to: {}".format(channel_name, percent))

        # Verify panel is not shutdown
        if self.is_shutdown:
            return Error("Unable to set output, panel is shutdown")

        # Verify panel is healthy
        if not self.health.healthy:
            return Error("Unable to set output, panel is unhealthy")

        # Convert channel name to channel number
        channel_number, error = self.get_channel_number(channel_name)

        # Check for errors
        if error.exists():
            error.report("Panel unable to set output")
            return error

        # Check if panel is healthy
        if not self.health.healthy:
            error = Error("Unable to set outputs, panel is not healthy")
            self.logger.debug(error.latest())

        # Set output on DAC
        error = self.dac5578.set_output(channel_number, percent)

        # Check for errors
        if error.exists():
            error.report("Panel unable to set output")
            return error
        
        # Success!
        self.logger.debug("Successfully set output")
        return Error(None)


    def set_outputs(self, outputs: dict) -> Error:
        """ Sets outputs on dac. Converts channel names to channel numbers 
            then sets outputs on dac. """
        self.logger.debug("Setting outputs: {}".format(outputs))

        # Verify panel is not shutdown
        if self.is_shutdown:
            return Error("Unable to set outputs, panel is shutdown")

        # Verify panel is healthy
        if not self.health.healthy:
            return Error("Unable to set outputs, panel is unhealthy")

        # Convert channel names to channel numbers
        converted_outputs = {}
        for name, percent in outputs.items():
            number, error = self.get_channel_number(name)

            # Check for errors
            if error.exists():
                error.report("Panel unable to set outputs")
                self.logger.debug(error.trace)
                return error

            # Append to converted outputs
            converted_outputs[number] = percent

        # Check if panel is healthy
        if not self.health.healthy:
            error = Error("Unable to set outputs, panel is not healthy")
            self.logger.debug(error.latest())

        # Set outputs on dacs
        error = self.dac5578.set_outputs(converted_outputs)

        # Check for errors
        if error.exists():
            error.report("Panel unable to set outputs")
            return error
        
        # Success!
        self.logger.debug("Successfully set outputs")
        return Error(None)


    def set_spd(self, desired_distance_cm: float, desired_intensity_watts: float, 
            desired_spectrum_nm_percent: dict) -> Tuple[Optional[dict], Optional[dict], Optional[dict], Error]:
        """ Sets spectral power distribution. Approximates spd, sets output 
            channels then returns output parameters and error status. """
        self.logger.debug("Setting spd, distance={}cm, intensity={}W, spectrum={}".format(
            desired_distance_cm, desired_intensity_watts, desired_spectrum_nm_percent))

        # Verify panel is not shutdown
        if self.is_shutdown:
            return Error("Unable to set spd, panel is shutdown")

        # Verify panel is healthy
        if not self.health.healthy:
            return Error("Unable to set spd, panel is unhealthy")

        # Approximate spectral power distribution
        try:
            channel_outputs, output_spectrum_nm_percent, output_intensity_watts = light.approximate_spd(
                channel_configs = self.channel_configs, 
                desired_distance_cm = desired_distance_cm, 
                desired_intensity_watts = desired_intensity_watts, 
                desired_spectrum_nm_percent = desired_spectrum_nm_percent,
            )
        except:
            error = Error("Panel unable to set spd due to approximate spd function failure")
            self.logger.exception(error.latest())
            return None, None, None, error

        # Set channel outputs
        error = self.set_outputs(channel_outputs)

        # Check for errors
        if error.exists():
            return None, None, None, error

        # Return output parameters and error status
        self.logger.debug("Successfully set spd, output: channels={}, spectrum={}, intensity={}W".format(
            channel_outputs, output_spectrum_nm_percent, output_intensity_watts))
        return channel_outputs, output_spectrum_nm_percent, output_intensity_watts, Error(None)


    def get_channel_number(self, channel_name: str) -> Tuple[Optional[int], Error]:
        """ Gets channel number from channel name. """
        
        # Look for channel name in channel configs
        for channel_config in self.channel_configs:
            if channel_config["name"]["brief"] == channel_name:
                channel_number = int(channel_config["channel"]["software"])
                return channel_number, Error(None)
       
        # Channel name not found
        error = Error("Unknown channel name: `{}`".format(channel_name))
        return None, error
