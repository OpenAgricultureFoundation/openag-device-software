# Import python modules
import threading

# Import peripheral parent class
from ..peripheral import Peripheral


class LightSpectrumIntensity(Peripheral):
    """ Parent class for light spectrum and intensity actuator """
    _spectrum = []
    _intensity = None
    _sampling_interval_sec = 0.2 # 200ms


    def initialize_peripheral_config(self):
        """ Initializes peripheral specific config. """
        self.spectrum_name = self.config["variables"]["spectrum"]["name"]
        self.intensity_name = self.config["variables"]["intensity"]["name"]
        self.pseudo_sensor_enabled = self.config["options"]["pseudo_sensor_enabled"]


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
            self.env.report_actuator_value(self.name, self.spectrum_name, self.spectrum)
            if self.pseudo_sensor_enabled:
                # Report simply since data is an array of ints
                self.env.report_sensor_value(self.name, self.spectrum_name, self.spectrum, simple=True)

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
            self.env.report_actuator_value(self.name, self.intensity_name,  self.intensity)
            if self.pseudo_sensor_enabled:
                self.env.report_sensor_value(self.name, self.intensity_name, self.intensity)


    def setup_peripheral(self):
        """ Setup peripheral. """

        self._intensity = None
        self._spectrum = None
        with threading.Lock():
            # Update intensity
            self.env.report_actuator_value(self.name, self.intensity_name,  self._intensity)
            if self.pseudo_sensor_enabled:
                self.env.report_sensor_value(self.name, self.intensity_name, self._intensity, simple=True)

            # Update spectrum
            self.env.report_actuator_value(self.name, self.spectrum_name, self._spectrum)
            if self.pseudo_sensor_enabled:
                self.env.report_sensor_value(self.name, self.spectrum_name, self._spectrum, simple=True)


    def initialize_peripheral(self):
        """ Initializes peripheral. """
        try:
            self.logger.debug("Initialized")
        except:
            self.logger.exception("Unable to initialize")
            self.state = self.states.ERROR
            self.error = self.errors.UNKNOWN


    def update_peripheral(self):
        """ Updates peripheral. """

        # Check for new desired spectrum and update if so
        if self.spectrum_name in self.env.sensor["desired"]:
            desired_spectrum = self.env.sensor["desired"][self.spectrum_name]
            if desired_spectrum != self.spectrum:
                self.set_spectrum(desired_spectrum)

        # Check for new desired intensity and update if so
        if self.intensity_name in self.env.sensor["desired"]:
            desired_intensity = self.env.sensor["desired"][self.intensity_name]
            if desired_intensity != self.intensity:
                self.set_intensity(desired_intensity)


    def reset_peripheral(self):
        """ Reset peripheral. """
        self.spectrum = None
        self.intensity = None
