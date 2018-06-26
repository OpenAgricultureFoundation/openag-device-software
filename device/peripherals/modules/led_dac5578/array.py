# Import standard python modules
from typing import Tuple, Optional, List
import time

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error
from device.utilities.health import Health

# Import peripheral utilities
from device.peripherals.utilities import light

# Import led panel
from device.peripherals.modules.led_dac5578.panel import LEDDAC5578Panel


class LEDDAC5578Array(object):
    """ An array of LED panels. """

    _is_shutdown: bool = False
    _min_health: float = 40.0
    channel_outputs: dict = {}

    def __init__(
        self,
        name: str,
        panel_configs: dict,
        channel_configs: dict,
        simulate: bool = False,
    ) -> None:
        """ Instantiates LED array. Assumes all panels have the same channel
            config. If that is not the case, consider using multiple arrays. """

        # Instantiate logger
        self.logger = Logger(name="Array({})".format(name), dunder_name=__name__)

        # Initialize panel and channel configs
        self.panel_configs = panel_configs
        self.channel_configs = channel_configs

        # Instantiate all panels in array
        self.panels: List[Panel] = []
        for panel_config in panel_configs:
            self.panels.append(
                LEDDAC5578Panel(
                    name=panel_config["name"],
                    channel_configs=channel_configs,
                    bus=int(panel_config["bus"]),
                    address=int(panel_config["address"], 16),
                    mux=int(panel_config["mux"], 16),
                    channel=int(panel_config["channel"]),
                    simulate=simulate,
                )
            )

        # Initialize light panel utility functions
        self.get_channel_number = self.panels[0].get_channel_number
        self.build_channel_outputs = self.panels[0].build_channel_outputs

    @property
    def health(self):
        """ Calculates health percentage from number of healthy panels over
            total number of panels. """
        num_healthy = len([panel for panel in self.panels if panel.healthy])
        return num_healthy / len(self.panels) * 100.0

    @property
    def healthy(self):
        """ Calculates healthyness by comparing health to min health. """
        return self.health > self._min_health

    @property
    def is_shutdown(self) -> bool:
        """ Returns device shutdown status from health or if manually set. """
        return self._is_shutdown or not self.healthy

    @is_shutdown.setter
    def is_shutdown(self, value: bool) -> bool:
        """ Shutsdown array. """
        self._is_shutdown = value

    def initialize(self) -> Error:
        """ Initializes array. Initializes all panels in array. """
        self.logger.debug("Initializing array")

        # Initialize all panels
        for panel in self.panels:

            # Try to initialize panel until successful or shuts down
            while not panel.is_shutdown:
                error = panel.initialize()

                # Check if successful
                if not error.exists():
                    break

        # Check if array became unhealthy
        if not self.healthy:
            error.report("Array unable to initialize")
            return error

        # Successfully initialized!
        self.logger.debug("Initialization successful")
        return Error(None)

    def shutdown(self):
        """ Shutsdown all panels in array. """
        # for panel in self.panels:
        #     panel.shutdown()
        self.is_shutdown = True

    def reset(self):
        """ Resets all panels in array. """
        for panel in self.panels:
            panel.reset()
        self.is_shutdown = False

    def set_output(self, channel_name: str, percent: float) -> Error:
        """ Sets output on all panels if not shutdown. """
        self.logger.debug(
            "Setting output on channel {} to: {}".format(channel_name, percent)
        )

        # Verify array is not shutdown
        if self.is_shutdown:
            return Error("Array unable to set output, array is shutdown")

        # Update stored channel outputs
        self.channel_outputs[channel_name] = percent

        # Set output on all panels
        for panel in self.panels:

            # Try to set ouput on panel until successful or shuts down
            while not panel.is_shutdown:
                error = panel.set_output(channel_name, percent)

                # Check if successful
                if not error.exists():
                    break

        # Check if array became unhealthy
        if not self.healthy:
            error.report("Array unable to set output, became too unhealthy")
            self.logger.error(error.latest())
            return error

        # Successfully set output!
        self.logger.debug("Set output successful")
        return Error(None)

    def set_outputs(self, outputs: dict) -> Error:
        """ Sets outputss on all panels if not shutdown. """
        self.logger.debug("Setting outputs on channel {}".format(outputs))

        # Verify array is not shutdown
        if self.is_shutdown:
            return Error("Array unable to set outputs, array is shutdown")

        # Update stored channel outputs
        self.channel_outputs = outputs

        # Check outputs are valid
        for name, percent in outputs.items():
            number, error = self.get_channel_number(name)

            # Check for errors
            if error.exists():
                error.report("Array unable to set outputs")
                self.logger.debug(error.trace)
                return error

        # Set outputs on all panels
        for panel in self.panels:

            # Try to set ouput on panel until successful or shuts down
            while not panel.is_shutdown:
                error = panel.set_outputs(outputs)

                # Check if successful
                if not error.exists():
                    break

        # Check if array became unhealthy
        if not self.healthy:
            error.report("Array unable to set outputs, became too unhealthy")
            self.logger.error(error.latest())
            return error

        # Successfully set outputs!
        self.logger.debug("Set outputs successful")
        return Error(None)

    def set_spd(
        self,
        desired_distance_cm: float,
        desired_intensity_watts: float,
        desired_spectrum_nm_percent: dict,
    ) -> Tuple[Optional[dict], Optional[dict], Optional[dict], Error]:
        """ Sets spectral power distribution. Approximates spd, sets output 
            channels then returns output parameters and error status. """
        self.logger.debug(
            "Setting spd, distance={}cm, intensity={}W, spectrum={}".format(
                desired_distance_cm,
                desired_intensity_watts,
                desired_spectrum_nm_percent,
            )
        )

        # Verify array is not shutdown
        if self.is_shutdown:
            return Error("Array unable to set outputs, array is shutdown")

        # Approximate spectral power distribution
        try:
            channel_outputs, output_spectrum_nm_percent, output_intensity_watts = light.approximate_spd(
                channel_configs=self.channel_configs,
                desired_distance_cm=desired_distance_cm,
                desired_intensity_watts=desired_intensity_watts,
                desired_spectrum_nm_percent=desired_spectrum_nm_percent,
            )
        except:
            error = Error(
                "Array unable to set spd due to approximate spd function failure"
            )
            self.logger.exception(error.latest())
            return None, None, None, error

        # Set channel outputs
        error = self.set_outputs(channel_outputs)

        # Check for errors
        if error.exists():
            return None, None, None, error

        # Return output parameters and error status
        self.logger.debug(
            "Successfully set spd, output: channels={}, spectrum={}, intensity={}W".format(
                channel_outputs, output_spectrum_nm_percent, output_intensity_watts
            )
        )
        return channel_outputs, output_spectrum_nm_percent, output_intensity_watts, Error(
            None
        )

    def turn_on(self, channel_name: Optional[str] = None) -> Error:
        """ Turns on all channels if no channel is specified. """

        # Set channel or channels
        if channel_name != None:
            self.logger.debug("Turning on channel: {}".format(channel_name))
            error = self.set_output(channel_name, 100)
        else:
            self.logger.debug("Turning on all channels")
            channel_outputs = self.build_channel_outputs(100)
            error = self.set_outputs(channel_outputs)

        # Check for errors
        if error.exists():
            error.report("Array unable to turn on")
            self.logger.error(error.latest())
            return error
        else:
            return Error(None)

    def turn_off(self, channel_name: Optional[str] = None) -> Error:
        """ Turns off all channels if no channel is specified. """

        # Set channel or channels
        if channel_name != None:
            self.logger.debug("Turning off channel: {}".format(channel_name))
            error = self.set_output(channel_name, 0)
        else:
            self.logger.debug("Turning off all channels")
            channel_outputs = self.build_channel_outputs(0)
            error = self.set_outputs(channel_outputs)

        # Check for errors
        if error.exists():
            error.report("Array unable to turn off")
            self.logger.error(error.latest())
            return error
        else:
            return Error(None)
