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
from device.peripherals.common.dac5578.driver import DAC5578


class LEDDAC5578Panel:
    """ An led panel controlled by a DAC5578. """

    # Initialize shutdown state
    _is_shutdown: bool = False

    def __init__(
        self,
        name,
        channel_configs,
        bus,
        address,
        mux=None,
        channel=None,
        simulate=False,
    ):
        """ Instantiates panel. """

        # Initialize logger
        self.logger = Logger(name="Panel({})".format(name), dunder_name=__name__)

        # Initialize name and channel configs
        self.name = name
        self.channel_configs = channel_configs

        # Initialize driver
        self.dac5578 = DAC5578(
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
        """ Returns healthyness from health manager. """
        return self.health.healthy

    @property
    def is_shutdown(self) -> bool:
        """ Returns device shutdown status from health or if manually set. """
        return self._is_shutdown or not self.healthy

    @is_shutdown.setter
    def is_shutdown(self, value: bool) -> bool:
        self._is_shutdown = value

    def initialize(self) -> Error:
        """ Initializes panel by probing driver with retry enabled. """
        self.logger.debug("Initializing panel")

        # Probe dac
        error = self.dac5578.probe()

        # Check for errors and update health
        if error.exists():
            error.report("Unable to initialize panel")
            self.health.report_failure()
            return error
        else:
            self.health.report_success()

        # Initialization successful!
        self.health.reset()
        self.logger.debug("Successfully initialized")
        return Error(None)

    def reset(self):
        """ Resets panel. """
        self.logger.debug("Resetting")
        self.health.reset()
        self.is_shutdown = False

    def shutdown(self):
        """ Shutdown panel. """
        self.logger.debug("Shutting down")
        self.is_shutdown = True

    def set_output(self, channel_name: str, percent: float) -> Error:
        """ Sets output on dac. Converts channel name to channel number 
            then sets output on dac. """
        self.logger.debug(
            "Setting output on channel {} to: {}".format(channel_name, percent)
        )

        # Check panel is not shutdown
        if self.is_shutdown:
            return Error("Unable to set output, panel is shutdown")

        # Convert channel name to channel number
        channel_number, error = self.get_channel_number(channel_name)

        # Check for errors
        if error.exists():
            error.report("Panel unable to set output")
            self.logger.error(error.latest())
            return error

        # Write to DAC until successful or too unhealthy
        while self.healthy:

            # Set output on DAC
            error = self.dac5578.write_output(channel_number, percent)

            # Check for errors and update health
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                self.health.reset()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Panel unable to set output, became too unhealthy")
            self.logger.error(error.latest())
            return error

        # Successfully set output!
        self.logger.debug("Successfully set output")
        return Error(None)

    def set_outputs(self, outputs: dict) -> Error:
        """ Sets outputs on dac. Converts channel names to channel numbers 
            then sets outputs on dac. """
        self.logger.debug("Setting outputs: {}".format(outputs))

        # Check panel is not shutdown
        if self.is_shutdown:
            return Error("Unable to set outputs, panel is shutdown")

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

        # Write to DAC until successful or too unhealthy
        while self.healthy:

            # Set outputs on DAC
            error = self.dac5578.write_outputs(converted_outputs, retries=5)

            # Check for errors and update health
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                self.health.reset()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Panel unable to set outputs, became too unhealthy")
            self.logger.error(error.latest())
            return error

        # Successfully set outputs!
        self.logger.debug("Successfully set outputs")
        return Error(None)

    def set_spd(
        self,
        desired_distance_cm: float,
        desired_ppfd_umol_m2_s: float,
        desired_spectrum_nm_percent: dict,
    ) -> Tuple[Optional[dict], Optional[dict], Optional[dict], Error]:
        """ Sets spectral power distribution. Approximates spd, sets output 
            channels then returns output parameters and error status. """
        self.logger.debug(
            "Setting spd, distance={}cm, ppfd={}umol/m2/s, spectrum={}".format(
                desired_distance_cm, desired_ppfd_umol_m2_s, desired_spectrum_nm_percent
            )
        )

        # Verify panel is not shutdown
        if self.is_shutdown:
            return Error("Unable to set spd, panel is shutdown")

        # Approximate spectral power distribution
        try:
            channel_outputs, output_spectrum_nm_percent, output_ppfd_umol_m2_s = light.approximate_spd(
                channel_configs=self.channel_configs,
                desired_distance_cm=desired_distance_cm,
                desired_ppfd_umol_m2_s=desired_ppfd_umol_m2_s,
                desired_spectrum_nm_percent=desired_spectrum_nm_percent,
            )
        except:
            error = Error(
                "Panel unable to set spd due to approximate spd function failure"
            )
            self.logger.exception(error.latest())
            return None, None, None, error

        # Set channel outputs
        error = self.set_outputs(channel_outputs)

        # Check for errors, no need to update health, handled in set outputs
        if error.exists():
            return None, None, None, error

        # Return output parameters and error status
        self.logger.debug(
            "Successfully set spd, output: channels={}, spectrum={}, ppfd={}umol/m2/s".format(
                channel_outputs, output_spectrum_nm_percent, output_ppfd_umol_m2_s
            )
        )
        return (
            channel_outputs,
            output_spectrum_nm_percent,
            output_ppfd_umol_m2_s,
            Error(None),
        )

    def turn_on(self, channel_name: Optional[str] = None) -> Error:
        """ Turns on all channels if no channel is specified. """

        # Check panel is not shutdown
        if self.is_shutdown:
            return Error("Unable to set outputs, panel is shutdown")

        # Set channel or channels
        if channel_name != None:
            self.logger.debug("Turning on channel: {}".format(channel_name))
            error = self.set_output(channel_name, 100)
        else:
            self.logger.debug("Turning on all channels")
            channel_outputs = self.build_channel_outputs(100)
            error = self.set_outputs(channel_outputs)

        # Check for errors, no need to update health, handled in set outputs
        if error.exists():
            error.report("Panel unable to turn on")
            self.logger.error(error.latest())
            return error
        else:
            return Error(None)

    def turn_off(self, channel_name: Optional[str] = None) -> Error:
        """ Turns off all channels if no channel is specified. """

        # Check panel is not shutdown
        if self.is_shutdown:
            return Error("Unable to set outputs, panel is shutdown")

        # Set channel or channels
        if channel_name != None:
            self.logger.debug("Turning off channel: {}".format(channel_name))
            error = self.set_output(channel_name, 0)
        else:
            self.logger.debug("Turning off all channels")
            channel_outputs = self.build_channel_outputs(0)
            error = self.set_outputs(channel_outputs)

        # Check for errors, no need to update health, handled in set outputs
        if error.exists():
            error.report("Panel unable to turn off")
            self.logger.error(error.latest())
            return error
        else:
            return Error(None)

    def fade(self, cycles: int, channel_name: Optional[str] = None) -> Error:
        """ Fades through all channels if no channel is specified. """
        self.logger.debug(
            "Fading {channel}".format(
                channel="all channels"
                if channel_name == None
                else "channel: " + channel_name
            )
        )

        # Check panel is not shutdown
        if self.is_shutdown:
            return Error("Unable to set outputs, panel is shutdown")

        # Turn off channels
        error = self.turn_off()

        # Check for errors, no need to update health
        if error.exists():
            error.report("Panel unable to fade")
            return error

        # Set channel or channels
        if channel_name != None:
            channel_names = [channel_name]
        else:
            channel_outputs = self.build_channel_outputs(0)
            channel_names = channel_outputs.keys()

        # Repeat for number of specified cycles
        for i in range(cycles):

            # Cycle through channels
            for channel_name in channel_names:

                # Fade up
                for value in range(0, 100, 10):
                    self.logger.info("Channel {}: {}%".format(channel_name, value))
                    error = self.set_output(channel_name, value)
                    if error.exists():
                        self.logger.warning("Error: {}".format(error.trace))
                        return error
                    time.sleep(0.1)

                # Fade down
                for value in range(100, 0, -10):
                    self.logger.info("Channel {}: {}%".format(channel_name, value))
                    error = self.set_output(channel_name, value)
                    if error.exists():
                        self.logger.warning("Error: {}".format(error.trace))
                        return error
                    time.sleep(0.1)

        return Error(None)

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

    def build_channel_outputs(self, value: float) -> dict:
        """ Build channel outputs. Sets each channel to provided value. """

        channel_outputs = {}
        for channel_config in self.channel_configs:
            name = channel_config["name"]["brief"]
            channel_outputs[name] = value
        return channel_outputs
