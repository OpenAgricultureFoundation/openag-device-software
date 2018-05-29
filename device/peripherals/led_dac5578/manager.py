# Import standard python modules
import threading
from typing import Optional

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.logger import Logger
from device.utilities.error import Error

# Import peripheral parent class
from device.peripherals.classes.manager import PeripheralManager

# Import led array
from device.peripherals.led_dac5578.array import LEDArray

# Import led events
from device.peripherals.led_dac5578.event_mixin import LEDEventMixin


class LEDManager(PeripheralManager, LEDEventMixin):
    """ Manages an LED array controlled by a dac5578. """

    _prev_desired_intensity = None
    _prev_desired_spectrum = None
    _prev_desired_distance = None


    def __init__(self, *args, **kwargs):
        """ Instantiates light array. Instantiates parent class, and initializes 
            sensor variable name. """

        # Instantiate parent class
        super().__init__(*args, **kwargs)

        # Initialize panel and channel configs
        self.panel_configs = self.parameters["communication"]["panels"]
        self.channel_configs = self.setup_dict["channel_configs"]

        # Initialize variable names
        self.intensity_name = self.parameters["variables"]["sensor"]["intensity_watts"]
        self.spectrum_name = self.parameters["variables"]["sensor"]["spectrum_nm_percent"]
        self.distance_name = self.parameters["variables"]["sensor"]["illumination_distance_cm"]
        self.channel_output_name = self.parameters["variables"]["actuator"]["channel_output_percents"]

        # Instantiate LED array
        self.array = LEDArray(self.name, self.panel_configs, self.channel_configs, self.simulate)

        # Initialize health, reset, and shutdown functions
        self.health = self.array.health
        self.reset = self.array.reset
        self.shutdown = self.array.shutdown


    def initialize(self) -> None:
        """ Initializes led manager. """
        self.logger.debug("Initializing")

        # Set initial parameters
        self.intensity = None
        self.spectrum = None
        self.distance = None

        # Initialize array
        error = self.array.initialize()

        # Check for errors
        if error.exists():
            error.report("Unable to initialize")
            self.logger.warning(error.trace)
            self.mode = Modes.ERROR
            return

        # Successful initialization!
        self.logger.debug("Initialized successfully")


    def setup(self) -> None:
        """ Sets up led manager. """
        self.logger.debug("Setting up")

        # Turn off all panels in array
        error = self.array.turn_off()

        # Check for errors
        if error.exists():
            error.report("Unable to setup")
            self.logger.warning(error.trace)
            self.mode = Modes.ERROR
            return

        # Successful setup!
        self.logger.debug("Setup successfully")


    def update(self) -> None:
        """ Updates led array if spectrum, intensity, or distance value changes. """

        # Initialize update flag
        update = False

        # Check for new desired intensity
        if self.desired_intensity != None and self.desired_intensity != self._prev_desired_intensity:
            self.logger.info("Received new desired intensity")
            self.logger.debug("desired_intensity = {} Watts".format(self.desired_intensity))
            update = True

        # Check for new desired spectrum
        if self.desired_spectrum != None and self.desired_spectrum != self._prev_desired_spectrum:
            self.logger.info("Received new desired spectrum")
            self.logger.debug("desired_spectrum_dict = {}".format(self.desired_spectrum))
            update = True

        # Check for new illumination distance
        if self.desired_distance != None and self.desired_distance != self._prev_desired_distance:
            self.logger.info("Received new desired illumination distance")
            self.logger.debug("desired_distance = {} cm".format(self.desired_distance))
            update = True

        # Check if update is required
        if not update:
            return

        # Verify all desired values exist:
        if self.desired_intensity == None or self.desired_spectrum == None or \
            self.desired_distance == None:
            self.logger.warning("Unable to update, not all desired values are set")
            return

        # Set spectral power distribution from desired values
        result = self.array.set_spd(
            desired_distance_cm = self.desired_distance_cm, 
            desired_intensity_watts = self.desired_intensity_watts, 
            desired_spectrum_nm_percent = self.desired_spectrum_nm_percent,
        )

        # Check for errors
        error = result[3]
        if error.exists():
            error.report("Unable to set spd")
            self.logger.warning(error.trace)
            self.mode = Modes.ERROR
            return

        # Update reported values
        self.channel_outputs = result[0]
        self.spectrum = result[1]
        self.intensity = result[2]

        # Update prev desired values
        self._prev_desired_intensity = self.desired_intensity
        self._prev_desired_spectrum = self.desired_spectrum
        self._prev_desired_distance = self.desired_distance

        # Successfully updated!
        self.logger.debug("Successfully updated")


    @property
    def spectrum(self) -> None:
        """ Gets spectrum value. """
        return self.state.get_peripheral_reported_sensor_value(self.name, self.spectrum_name)


    @spectrum.setter
    def spectrum(self, value: dict) -> None:
        """ Sets spectrum value in shared state. """
        self.state.set_environment_reported_sensor_value(self.name, self.spectrum_name, value, simple=True)
        self.state.set_peripheral_reported_sensor_value(self.name, self.spectrum_name, value)


    @property
    def desired_spectrum(self) -> dict:
        """ Gets desired spectrum value from shared environment state if not 
            in manual mode, otherwise gets it from peripheral state. """
        if self.mode != Modes.MANUAL:
            return self.state.get_environment_desired_sensor_value(self.spectrum_name)
        else:
            return self.state.get_peripheral_desired_sensor_value(self.name, self.spectrum_name)


    @property
    def intensity(self) -> float:
        """ Gets intensity value. """
        return self.state.get_peripheral_reported_sensor_value(self.name, self.intensity_name)


    @intensity.setter
    def intensity(self, value: float) -> None:
        """ Sets intensity value in shared state. """
        self.state.set_environment_reported_sensor_value(self.name, self.intensity_name, value, simple=True)
        self.state.set_peripheral_reported_sensor_value(self.name, self.intensity_name, value)


    @property
    def desired_intensity(self) -> float:
        """ Gets desired intensity value from shared environment state if not 
            in manual mode, otherwise gets it from peripheral state. """
        if self.mode != Modes.MANUAL:
            return self.state.get_environment_desired_sensor_value(self.intensity_name)
        else:
            return self.state.get_peripheral_desired_sensor_value(self.name, self.intensity_name)


    @property
    def distance(self) -> float:
        """ Gets distance value. """
        return self.state.get_peripheral_reported_sensor_value(self.name, self.distance_name)


    @distance.setter
    def distance(self, value: float) -> None:
        """ Sets distance value in shared state. """
        self.state.set_environment_reported_sensor_value(self.name, self.distance_name, value, simple=True)
        self.state.set_peripheral_reported_sensor_value(self.name, self.distance_name, value)


    @property
    def desired_distance(self) -> float:
        """ Gets desired distance value from shared environment state if not 
            in manual mode, otherwise gets it from peripheral state. """
        if self.mode != Modes.MANUAL:
            return self.state.get_environment_desired_sensor_value(self.distance_name)
        else:
            return self.state.get_peripheral_desired_sensor_value(self.name, self.distance_name)


    @property
    def channel_outputs(self) -> dict:
        """ Gets distance value. """
        return self.state.get_peripheral_reported_actuator_value(self.name, self.channel_output_name)


    @channel_outputs.setter
    def channel_outputs(self, value: dict) -> None:
        """ Sets channel outputs value in shared state. """
        self.logger.debug("Reporting channel outputs")
        self.state.set_environment_reported_actuator_value(self.name, self.channel_outputs_name, value)
        self.state.set_peripheral_reported_actuator_value(self.name, self.channel_outputs_name, value)


    @property
    def desired_channel_outputs(self) -> dict:
        """ Gets desired distance value from shared environment state if not 
            in manual mode, otherwise gets it from peripheral state. """
        if self.mode != Modes.MANUAL:
            return self.state.get_environment_desired_actuator_value(self.channel_output_name)
        else:
            return self.state.get_peripheral_desired_actuator_value(self.name, self.channel_output_name)