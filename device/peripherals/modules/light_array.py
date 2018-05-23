# Import standard python modules
import logging, time, threading, json

# Import peripheral parent class
from device.peripherals.classes.peripheral import Peripheral

# Import drivers
from device.drivers.dac5578 import DAC5578

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.errors import Errors
from device.utilities.health import Health


class LightArray(Peripheral):
    """ A light array of panels with DAC5578s controlling light output. """


    def __init__(self, *args, **kwargs):
        """ Instantiates light array. Instantiates parent class, and initializes 
            sensor variable name. """

        # Instantiate parent class
        super().__init__(*args, **kwargs)

        # Get device parameters
        self.panels = self.parameters["communication"]["panels"]

        # Initialize panel drivers
        self.dac5578s = []
        for panel in self.panels:
            dac5578 = DAC5578(
                name = panel["name"],
                bus = panel["bus"],
                address = int(panel["address"], 16), 
                mux = int(panel["mux"], 16), 
                channel = panel["channel"],
            )
            self.dac5578s.append(dac5578)

        # Initialize variable names
        self.intensity_name = self.parameters["variables"]["sensor"]["intensity_watts"]
        self.spectrum_name = self.parameters["variables"]["sensor"]["spectrum_channel_percents"]
        self.illumination_distance_name = self.parameters["variables"]["sensor"]["illumination_distance_cm"]
        self.channel_output_name = self.parameters["variables"]["actuator"]["channel_output_percents"]

        # Initialize channel configs
        self.load_channel_configs()
        self.parse_channel_configs()

        # Initialize health parameter
        self.health = Health(health_minimum=80, health_updates=10)


    def initialize(self):
        """ Initializes light array. Performs initial health check.
            Finishes within 200ms.  """

        # Initialize sensor
        self.logger.debug("Initializing")

        # Set initial parameters
        self.intensity = None
        self.spectrum = None
        self.distance = None

        # Probe health
        self.probe() 


    def setup(self):
        """ Sets up actuator. Useful for actuators with warm up times >200ms """
        self.logger.debug("Setting up sensor")

        # Setup sensor
        try:    
           # Start with light panel off
            self.turn_off_output()
            self.logger.debug("Successfully setup sensor")
        except:
            self.logger.exception("Sensor setup failed")
            self.mode = Modes.ERROR


    def update(self):
        """ Updates actuator. """

        # Initialize channel update flag
        update_channels = False

        # Check for new desired intensity
        if self.desired_intensity != self.intensity and self.desired_intensity != None:
            self.logger.info("Received new desired intensity")
            self.logger.debug("desired_intensity = {} Watts".format(self.desired_intensity))
            update_channels = True

        # Check for new desired spectrum
        if self.desired_spectrum != self.spectrum:
            self.logger.info("Received new desired spectrum")
            self.logger.debug("desired_spectrum_dict = {}".format(self.desired_spectrum))
            update_channels = True

        # Check for new illumination distance
        if self.desired_distance != self.distance:
            self.logger.info("Received new desired illumination distance")
            self.logger.debug("desired_illumination_distance = {} cm".format(self.desired_distance))
            update_channels = True

        # Update output channels if new value
        if update_channels:
            self.update_channel_outputs()


    def reset(self):
        """ Resets sensor. """
        self.logger.info("Resetting sensor")

        # Reset peripheral health & clear error
        self.health.reset()
        self.error = None

        # Reset driver health
        for dac5578 in self.dac5578s:
            dac5578.health.reset()

        # Clear reported values
        self.clear_reported_values()

        # Reset complete!
        self.logger.debug("Successfully reset sensor")


    def shutdown(self):
        """ Shuts down actuator. """

        # Reset driver health
        for dac5578 in self.dac5578s:
            dac5578.health.reset()

        # Clear reported values
        self.clear_reported_values()

        # Send enable sleep command to actuator hardware
        try:
            self.turn_off_output()
            self.logger.debug("Successfully shutdown actuator")
        except:
            self.logger.exception("Actuator shutdown failed")
            self.mode = Modes.ERROR









    def clear_reported_values(self):
        """ Clears values reported to shared state. """
        self.intensity = None
        self.spectrum = None
        self.distance = None


    def load_channel_configs(self): 
        """ Loads channel configs from setup file. """
        self.logger.debug("Loading channel configs")
        self.channel_configs = self.setup_dict["channel_configs"]


    def parse_channel_configs(self):
        """ Parses channel configs. """
        self.logger.debug("Parsing channel configs")

        self.channel_config_dict = {}
        for channel_config in self.channel_configs:
            channel_key = channel_config["name"]["brief"]
            self.channel_config_dict[channel_key] = channel_config








    @property
    def spectrum(self):
        """ Gets spectrum value. """
        try:
            return self._spectrum
        except NameError:
            self._spectrum = None
            return self._spectrum


    @spectrum.setter
    def spectrum(self, value):
        """ Safely updates spectrum in environment object each time
            it is changed. """
        self._spectrum = value
        self.report_sensor_value(self.name, self.spectrum_name, value, simple=True)
        self.report_peripheral_sensor_value(self.spectrum_name, value)


    @property
    def desired_spectrum(self):
        """ Gets desired spectrum value from shared environment state if not 
            in manual mode, otherwise gets it from peripheral state. """

        if self.mode != Modes.MANUAL:
            if "sensor" not in self.state.environment:
                return
            if "desired" not in self.state.environment["sensor"]:
                return
            if self.spectrum_name in self.state.environment["sensor"]["desired"]:
                value = self.state.environment["sensor"]["desired"][self.spectrum_name]
                return value
        else:
            if "stored" not in self.state.peripherals:
                return
            if "desired" not in self.state.peripherals["stored"]:
                return
            if self.spectrum_name in self.state.peripherals[self.name]["stored"]["desired"]:
                value = self.state.environment["sensor"]["desired"][self.spectrum_name]
                return value


    @desired_spectrum.setter
    def desired_spectrum(self, value):
        """ Safely updates desired spectrum in shared peripheral state. Only 
            updates from manual mode. """

        # Verify only setting from manual mode
        if self.mode != Modes.MANUAL:
            self.logger.error("desired_intensity setter should only be set from manual mode")
            return

        # Safely write desired intensity to shared peripheral state
        with threading.Lock():
            if "stored" not in self.state.peripherals[self.name]:
                self.state.peripherals[self.name]["stored"] = {}
            if "desired" not in self.state.peripherals[self.name]["stored"]:
                self.state.peripherals[self.name]["stored"]["desired"] = {}
            self.state.peripherals[self.name]["stored"]["desired"][self.spectrum_name] = value


    @property
    def intensity(self):
        """ Gets intensity value. """
        try:
            return self._intensity
        except NameError:
            self._intensity = None
            return self._intensity


    @intensity.setter
    def intensity(self, value):
        """ Safely updates intensity in environment object each time 
            it is changed. """
        self._intensity = value
        self.report_sensor_value(self.name, self.intensity_name, value, simple=True)
        self.report_peripheral_sensor_value(self.intensity_name, value)

    @property
    def desired_intensity(self):
        """ Gets desired intensity value from shared environment state if not 
            in manual mode, otherwise gets it from peripheral state. """

        if self.mode != Modes.MANUAL:
            if "sensor" not in self.state.environment:
                return
            if "desired" not in self.state.environment["sensor"]:
                return
            if self.intensity_name in self.state.environment["sensor"]["desired"]:
                value = self.state.environment["sensor"]["desired"][self.intensity_name]
                return value
        else:
            if "stored" not in self.state.peripherals:
                return
            if "desired" not in self.state.peripherals["stored"]:
                return
            if self.intensity_name in self.state.peripherals[self.name]["stored"]["desired"]:
                value = self.state.environment["sensor"]["desired"][self.intensity_name]
                return value


    @desired_intensity.setter
    def desired_intensity(self, value):
        """ Safely updates desired intensity in shared peripheral state. Only 
            updates from manual mode. """

        # Verify only setting from manual mode
        if self.mode != Modes.MANUAL:
            self.logger.error("desired_intensity setter should only be set from manual mode")
            return

        # Safely write desired intensity to shared peripheral state
        with threading.Lock():
            if "stored" not in self.state.peripherals[self.name]:
                self.state.peripherals[self.name]["stored"] = {}
            if "desired" not in self.state.peripherals[self.name]["stored"]:
                self.state.peripherals[self.name]["stored"]["desired"] = {}
            self.state.peripherals[self.name]["stored"]["desired"][self.intensity_name] = value


    @property
    def distance(self):
        """ Gets intensity value. """
        try:
            return self._distance
        except NameError:
            self._distance = None
            return self._distance


    @distance.setter
    def distance(self, value):
        """ Safely updates illumination distance in environment object each time 
            it is changed. """
        self._distance = value
        self.report_sensor_value(self.name, self.illumination_distance_name, value, simple=True)
        self.report_peripheral_sensor_value(self.illumination_distance_name, value)


    @property
    def desired_distance(self):
        """ Gets desired illumination distance value from shared environment state if not 
            in manual mode, otherwise gets it from peripheral state. """

        if self.mode != Modes.MANUAL:
            if "sensor" not in self.state.environment:
                return
            if "desired" not in self.state.environment["sensor"]:
                return
            if self.illumination_distance_name in self.state.environment["sensor"]["desired"]:
                value = self.state.environment["sensor"]["desired"][self.illumination_distance_name]
                return value
        else:
            if "stored" not in self.state.peripherals:
                return
            if "desired" not in self.state.peripherals["stored"]:
                return
            if self.illumination_distance_name in self.state.peripherals[self.name]["stored"]["desired"]:
                value = self.state.environment["sensor"]["desired"][self.illumination_distance_name]
                return value


    @desired_distance.setter
    def desired_distance(self, value):
        """ Safely updates desired intensity in shared peripheral state. Only 
            updates from manual mode. """

        # Verify only setting from manual mode
        if self.mode != Modes.MANUAL:
            self.logger.error("desired_intensity setter should only be set from manual mode")
            return

        # Safely write desired intensity to shared peripheral state
        with threading.Lock():
            if "stored" not in self.state.peripherals[self.name]:
                self.state.peripherals[self.name]["stored"] = {}
            if "desired" not in self.state.peripherals[self.name]["stored"]:
                self.state.peripherals[self.name]["stored"]["desired"] = {}
            self.state.peripherals[self.name]["stored"]["desired"][self.illumination_distance_name] = value


    @property
    def channel_outputs(self):
        """ Gets channel outputs percent value. """
        try:
            return self._channel_outputs
        except NameError:
            self._channel_outputs = None
            return self._channel_outputs


    @channel_outputs.setter
    def channel_outputs(self, value):
        """ Safely updates channel outputs percent in environment object each time 
            it is changed. """
        self._channel_outputs = value
        self.report_actuator_value(self.name, self.channel_output_name, value)
        self.set_desired_actuator_value(self.name, self.channel_output_name, value)

        self.report_peripheral_actuator_value(self.channel_output_name, value)
