# Import standard python modules
from typing import Tuple, Optional, List

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error
from device.utilities.health import Health

# Import led panel
from device.peripherals.led_dac5578.panel import LEDPanel


# TODO: Handle shutdown case


class LEDArray:

    def __init__(self, name: str, panel_configs: dict, channel_configs: dict, 
            simulate: bool = False) -> None:
        """ Instantiates LED array. Assumes all panels have the same channel
            config. If that is not the case, consider using multiple arrays. """

        # Instantiate logger
        self.logger = Logger(
            name = "LEDArray({})".format(name),
            dunder_name = __name__,
        )

        # Initialize panel and channel configs
        self.panel_configs = panel_configs
        self.channel_configs = channel_configs

        # Instantiate all panels in array
        self.panels: List[LEDPanel] = []
        for panel_config in panel_configs:
            self.panels.append(LEDPanel(
                name = panel_config["name"], 
                channel_configs = channel_configs,
                bus = panel_config["bus"], 
                address = panel_config["address"],
                mux = panel_config["mux"], 
                channel = panel_config["channel"],
                simulate = simulate,
            ))

        # Instantiate health
        self.health = Health(updates=5, minimum=60)


    def initialize(self):
        """ Initializes array. Initializes all panels in array. """
        for panel in self.panels:
            panel.initialize()


    def probe(self, retry: bool = False) -> Error:
        """ Probes all panels in array, updates array health from 
            aggregate panel health. """
        self.logger.debug("Probing, retry = {}".format(retry))

        # Probe all panels
        panel_error_traces = []
        for panel in self.panels:
            error = panel.probe(retry=retry)
    
            # Check for error and update health
            if error.exists():
                panel_error_traces.append(error.trace)
                self.health.report_failure()
            else:
                self.health.report_success()

        # Log errors for now. TODO: do something smarter
        self.logger.debug("panel_error_traces = {}".format(panel_error_traces))

        # Check if array is still healthy and return
        if not self.health.healthy:
            error = Error("Unacceptable array health after probe")
            return error

        # Healthy!
        self.logger.debug("Probe successful")
        return Error(None)


    def set_output(self, channel_name: str, percent: float) -> Error:
        """ Sets output on all panels if not shutdown. """
        self.logger.debug("Setting output on channel {} to: {}".format(channel_name, percent))

        # TODO: Check if array is healthy

        # Set output on all panels
        for panel in self.panels:

            # TODO: Check if panel is healthy

            # Set output on pannel
            error = panel.set_output(channel_name, percent)

            # Check for error and update health
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()

        # Check if array is still healthy and return
        if not self.health.healthy:
            error = Error("Unacceptable array health after set output")
            return error

        # Healthy!
        self.logger.debug("Set output successful")
        return Error(None)


    def set_outputs(self, outputs: dict) -> Error:
        """ Sets outputss on all panels if not shutdown. """
        self.logger.debug("Setting outputs on channel {}".format(outputs))

        # Check outputs are valid
        for name, percent in outputs.items():
            number, error = self.get_channel_number(name)

            # Check for errors
            if error.exists():
                error.report("Array unable to set outputs")
                self.logger.debug(error.trace)
                return error

        # Check if array is healthy
        if not self.health.healthy:
            error = Error("Unable to set outputs, array is not healthy")
            self.logger.debug(error.latest())

        # Set output on all panels that are healthy
        for panel in self.panels:

            # Skip setting on unhealthy panels
            if not panel.health.healthy:
                break

            # Set output on pannel
            error = panel.set_outputs(outputs)

            # Check for error and update health
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()

        # Check if array is still healthy and return
        if not self.health.healthy:
            error = Error("Unacceptable array health after set outputs")
            return error

        # Healthy!
        self.logger.debug("Set outputs successful") 
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
        channel_outputs = {}
        for channel_config in self.channel_configs:
            name = channel_config["name"]["brief"]
            channel_outputs[name] = value
        return channel_outputs


    def turn_off(self) -> Error:
        """ Turns off light panel. """  
        self.logger.debug("Turning off")

        # Build channel outputs and set
        channel_outputs = self.build_channel_outputs(0)
        error = self.set_outputs(channel_outputs)

        # Check for errors
        if error.exists():
            error.report("Unable to turn off")
            self.logger.debug(error.trace)
            return error

        # Successfully turned off
        self.logger.debug("Successfully turned off")
        return Error(None)
        


        


