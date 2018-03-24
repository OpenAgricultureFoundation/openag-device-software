# Import python modules
import threading

# Import peripheral parent class
from peripheral.utility.actuator.light_spectrum_intensity import LightSpectrumIntensity


class LightPanelTaurus(LightSpectrumIntensity):
    """ A light panel with six independently controlled channels that can 
    create the Taurus light spectrum. """


    def set_spectrum(self, spectrum):
        """ Set light spectrum. """
        try:
            self.spectrum = spectrum
            self.logger.debug("Set spectrum: {}".format(self.spectrum))
        except:
            self.logger.exception("Unable to set spectrum")
            self.state = self.states.ERROR
            self.error = self.errors.UNKNOWN
    

    def set_intensity(self, intensity):
        """ Set light intensity. """
        try:
            self.intensity = intensity
            self.logger.debug("Set intensity: {}".format(self.intensity))
        except:
            self.logger.exception("Unable to set intensity")
            self.state = self.states.ERROR
            self.error = self.errors.UNKNOWN