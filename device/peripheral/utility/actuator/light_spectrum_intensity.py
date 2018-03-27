# Import python modules
import threading

# Import device modes, errors, and variables
from device.utility.mode import Mode
from device.utility.error import Error
from device.utility.variable import Variable

# Import peripheral parent class
from ..peripheral import Peripheral


class LightSpectrumIntensity(Peripheral):
    """ Parent class for light spectrum and intensity actuator """
    _spectrum = None
    _intensity = None


    @property
    def spectrum(self):
        """ Gets spectrum value. """
        return self._spectrum


    @spectrum.setter
    def spectrum(self, value):
        """ Safely updates spectrum in environment object each time
            it is changed. """
        self._spectrum = value
        with threading.Lock():
            self.report_actuator_value(self.name, self.spectrum_name, self.spectrum)
            if self.pseudo_sensor_enabled:
                # Report simply since data is an array of ints
                self.report_sensor_value(self.name, self.spectrum_name, self.spectrum, simple=True)

    @property
    def intensity(self):
        """ Gets intensity value. """
        return self._intensity


    @intensity.setter
    def intensity(self, value):
        """ Safely updates intensity in environment object each time 
            it is changed. """
        self._intensity = value
        with threading.Lock():
            self.report_actuator_value(self.name, self.intensity_name,  self.intensity)
            if self.pseudo_sensor_enabled:
                self.report_sensor_value(self.name, self.intensity_name, self.intensity)


    def initialize_state(self):
        """ Initializes peripheral state. """
        self.logger.debug("{}: Initializing state".format(self.name))
        config = self.state.device["config"]["peripherals"][self.name]
        self.bus = config["communication"]["bus"]
        self.mux = config["communication"]["mux"]
        self.channel = config["communication"]["channel"]
        self.address = config["communication"]["address"]
        self.spectrum_name = config["variables"]["spectrum"]["name"]
        self.intensity_name = config["variables"]["intensity"]["name"]
        self.pseudo_sensor_enabled = config["options"]["pseudo_sensor_enabled"]

        self.spectrum = None
        self.intensity = None


    def update_peripheral(self):
        """ Updates peripheral. """

        # Check for new desired spectrum and update if so
        if self.spectrum_name in self.state.environment["sensor"]["desired"]:
            desired_spectrum = self.state.environment["sensor"]["desired"][self.spectrum_name]
            if desired_spectrum != self.spectrum:
                self.set_spectrum(desired_spectrum)

        # Check for new desired intensity and update if so
        if self.intensity_name in self.state.environment["sensor"]["desired"]:
            desired_intensity = self.state.environment["sensor"]["desired"][self.intensity_name]
            if desired_intensity != self.intensity:
                self.set_intensity(desired_intensity)


    def clear_reported_values(self):
        """ Clears reported values. """
        self.logger.debug("{}: Clearing reported values".format(self.name))
        self.spectrum = None
        self.intensity = None
