# Import python modules
import threading

# Import device modes, errors, and variables
from device.utility.mode import Mode
from device.utility.error import Error
from device.utility.variable import Variable

# Import peripheral parent class
from device.peripheral.utility.actuator.light_spectrum_intensity import LightSpectrumIntensity


class LightPanelTaurus(LightSpectrumIntensity):
    """ A light panel with six independently controlled channels that can 
    create the Taurus light spectrum. """

    def quickly_check_hardware_state(self):
        """ Quickly check hardware state. """
        pass


    def initialize_hardware(self):
        """ Initialize hardware. """
        pass


    def set_spectrum(self, spectrum):
        """ Set light spectrum. """
        try:
            self.spectrum = spectrum
            self.logger.debug("Set spectrum: {}".format(self.spectrum))
        except:
            self.logger.exception("Unable to set spectrum")
            self.mode = Mode.ERROR
            self.error = Error.UNKNOWN
    

    def set_intensity(self, intensity):
        """ Set light intensity. """
        try:
            self.intensity = intensity
            self.logger.debug("Set intensity: {}".format(self.intensity))
        except:
            self.logger.exception("Unable to set intensity")
            self.mode = Mode.ERROR
            self.error = Error.UNKNOWN