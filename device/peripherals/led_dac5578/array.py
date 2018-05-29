# Import standard python modules
from typing import Tuple, Optional, List

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error
from device.utilities.health import Health

# Import peripheral utilities
from device.peripherals.utilities import light

# Import led panel
from device.peripherals.led_dac5578.panel import LEDPanel


class LEDArray:

    # Initialize shutdown state
    is_shutdown: bool = False


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


        self.logger.debug("panel_configs = {}".format(panel_configs))

        # Instantiate all panels in array
        self.panels: List[LEDPanel] = []
        for panel_config in panel_configs:
            self.panels.append(LEDPanel(
                name = panel_config["name"], 
                channel_configs = channel_configs,
                bus = int(panel_config["bus"]), 
                address = int(panel_config["address"], 16),
                mux = int(panel_config["mux"], 16), 
                channel = int(panel_config["channel"]),
                simulate = simulate,
            ))

        # Instantiate health
        self.health = Health(updates=5, minimum=60)

        # Initialize light panel utility functions
        self.get_channel_number = self.panels[0].get_channel_number
        self.build_channel_outputs = self.panels[0].build_channel_outputs


    def initialize(self) -> Error:
        """ Initializes array. Initializes all panels in array. """
        self.logger.debug("Initializing array")

        # Initialize all panels
        panel_error_traces = []
        for panel in self.panels:
            error = panel.initialize()

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
            error = Error("Unacceptable array health after initialization")
            return error

        # Healthy!
        self.logger.debug("Initialization successful")
        return Error(None)


    def shutdown(self):
        """ Shutsdown all panels in array. """
        for panel in self.panels:
            panel.shutdown()
        self.is_shutdown = True


    def reset(self):
        """ Resets all panels in array. """
        for panel in self.panels:
            panel.reset()
        self.is_shutdown = False


    def set_output(self, channel_name: str, percent: float) -> Error:
        """ Sets output on all panels if not shutdown. """
        self.logger.debug("Setting output on channel {} to: {}".format(channel_name, percent))

        # Verify array is not shutdown
        if self.is_shutdown:
            return Error("Unable to set output, array is shutdown")

        # Verify array is healthy
        if not self.health.healthy:
            return Error("Unable to set output, array is unhealthy")

        # Set output on all panels
        for panel in self.panels:

            # Only set outputs on healthy, non-shutdown panels
            if not panel.health.healthy or panel.is_shutdown:
                continue

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

        # Verify array is not shutdown
        if self.is_shutdown:
            return Error("Unable to set outputs, array is shutdown")

        # Verify array is healthy
        if not self.health.healthy:
            return Error("Unable to set outputs, array is unhealthy")

        # Check outputs are valid
        for name, percent in outputs.items():
            number, error = self.get_channel_number(name)

            # Check for errors
            if error.exists():
                error.report("Array unable to set outputs")
                self.logger.debug(error.trace)
                return error

        # Set output on all panels that are healthy
        for panel in self.panels:

            # Only set outputs on healthy, non-shutdown panels
            if not panel.health.healthy or panel.is_shutdown:
                continue

            # Set output on panel
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
        self.logger.debug("Successfully set outputs") 
        return Error(None)


    def set_spd(self, desired_distance_cm: float, desired_intensity_watts: float, 
            desired_spectrum_nm_percent: dict) -> Tuple[Optional[dict], Optional[dict], Optional[dict], Error]:
        """ Sets spectral power distribution. Approximates spd, sets output 
            channels then returns output parameters and error status. """
        self.logger.debug("Setting spd, distance={}cm, intensity={}W, spectrum={}".format(
            desired_distance_cm, desired_intensity_watts, desired_spectrum_nm_percent))

        # Verify array is not shutdown
        if self.is_shutdown:
            return Error("Unable to set outputs, array is shutdown")

        # Verify array is healthy
        if not self.health.healthy:
            return Error("Unable to set outputs, array is unhealthy")

        # Approximate spectral power distribution
        try:
            channel_outputs, output_spectrum_nm_percent, output_intensity_watts = light.approximate_spd(
                channel_configs = self.channel_configs, 
                desired_distance_cm = desired_distance_cm, 
                desired_intensity_watts = desired_intensity_watts, 
                desired_spectrum_nm_percent = desired_spectrum_nm_percent,
            )
        except:
            error = Error("Array unable to set spd due to approximate spd function failure")
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


    def turn_on(self) -> Error:
        """ Turns off light panel. """  
        self.logger.debug("Turning on")

        # Build channel outputs and set to 100%
        channel_outputs = self.build_channel_outputs(100)
        error = self.set_outputs(channel_outputs)

        # Check for errors
        if error.exists():
            error.report("Unable to turn on")
            self.logger.debug(error.trace)
            return error

        # Successfully turned off
        self.logger.debug("Successfully turned on")
        return Error(None)


    def turn_off(self) -> Error:
        """ Turns off light panel. """  
        self.logger.debug("Turning off")

        # Build channel outputs and set to 0%
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

































# def fade_concurrently(self):
#     """ Fades output concurrently forever. Exits on new event. """
#     self.logger.debug("Fading concurrently")

#     # Use previously used illumination distance or first distance in entry if prev is none
#     if self.distance == None:
#         self.distance = self.channel_configs[0]["planar_distance_map"][0]["z_cm"]  


#     # Run fade loop until new event
#     while True:

#         # Fade up
#         for output_percent in range(0, 100, 10):
#             self.intensity = output_percent
#             channel_outputs = self.build_channel_outputs(output_percent)
#             self.set_channel_outputs(channel_outputs)
#             self.intensity, self.spectrum = self.calculate_output_intensity_and_spectrum(channel_outputs, self.distance)

#             # Check for events
#             if self.request != None:
#                 request = self.request
#                 self.request = None
#                 self.process_event(request)
#                 return

#             # Update every 100ms
#             time.sleep(0.1)

#         # Fade down
#         for output_percent in range(100, 0, -10):
#             self.intensity = output_percent
#             channel_outputs = self.build_channel_outputs(output_percent)
#             self.set_channel_outputs(channel_outputs)
#             self.intensity, self.spectrum = self.calculate_output_intensity_and_spectrum(channel_outputs, self.distance)


#             # Check for events
#             if self.request != None:
#                 request = self.request
#                 self.request = None
#                 self.process_event(request)
#                 return

#             # Update every 100ms
#             time.sleep(0.1)


# def fade_sequentially(self):
#     """ Fades output sequentially, forever. Exits on new event. """
#     self.logger.debug("Fading sequentially")

#     # Use previously used illumination distance or first distance in entry if prev is none
#     if self.distance == None:
#         self.distance = self.channel_configs[0]["planar_distance_map"][0]["z_cm"]  

#     # Run fade loop until new event
#     while True:

#         for channel_config in self.channel_configs:
#             channel_name = channel_config["name"]["brief"]
#             # Fade up
#             for output_percent in range(0, 100, 10):
#                 self.intensity = output_percent
#                 channel_outputs = self.build_channel_outputs(output_percent, enable_channel_name=channel_name)
#                 self.set_channel_outputs(channel_outputs)
#                 self.intensity, self.spectrum = self.calculate_output_intensity_and_spectrum(channel_outputs, self.distance)

#                 # Check for events
#                 if self.request != None:
#                     request = self.request
#                     self.request = None
#                     self.process_event(request)
#                     return

#                 # Update every 100ms
#                 time.sleep(0.1)

#             # Fade down
#             for output_percent in range(100, 0, -10):
#                 self.intensity = output_percent
#                 channel_outputs = self.build_channel_outputs(output_percent, enable_channel_name=channel_name)
#                 self.set_channel_outputs(channel_outputs)
#                 self.intensity, self.spectrum = self.calculate_output_intensity_and_spectrum(channel_outputs, self.distance)


#                 # Check for events
#                 if self.request != None:
#                     request = self.request
#                     self.request = None
#                     self.process_event(request)
#                     return

#                 # Update every 100ms
#                 time.sleep(0.1)


# def fade_channel_output(self, channel_name):
#     """ Fades output channel forever. Exits on new event. """
#     self.logger.debug("Fading channel")

#     # Turn off all channels
#     self.turn_off_output()

#     # Use previously used illumination distance or first distance in entry if prev is none
#     if self.distance == None:
#         self.distance = self.channel_configs[0]["planar_distance_map"][0]["z_cm"]  

#     # Run fade loop until new event
#     while True:

#         # Fade up
#         for output_percent in range(0, 100, 10):
#             self.intensity = output_percent
#             self.channel_outputs[channel_name] = output_percent # TODO: copy the dict and pass in, dont need to set twice (here + in set function)
#             self.set_channel_outputs(self.channel_outputs)
#             self.intensity, self.spectrum = self.calculate_output_intensity_and_spectrum(self.channel_outputs, self.distance)

#             # Check for events
#             if self.request != None:
#                 request = self.request
#                 self.request = None
#                 self.process_event(request)
#                 return

#             # Update every 100ms
#             time.sleep(0.1)

#         # Fade down
#         for output_percent in range(100, 0, -10):
#             self.intensity = output_percent
#             self.channel_outputs[channel_name] = output_percent # TODO: copy the dict and pass in, dont need to set twice (here + in set function)
#             self.set_channel_outputs(self.channel_outputs)
#             self.intensity, self.spectrum = self.calculate_output_intensity_and_spectrum(self.channel_outputs, self.distance)

#             # Check for events
#             if self.request != None:
#                 request = self.request
#                 self.request = None
#                 self.process_event(request)
#                 return

#             # Update every 100ms
#             time.sleep(0.1)