# Import python modules
import logging

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
        self.logger.debug("Quickly checking hardware state")


    def initialize_hardware(self):
        """ Initialize hardware. """
        self.logger.debug("Initializing hardware")


    def set_spectrum(self, spectrum):
        """ Set light spectrum. """
        try:
            self.spectrum = spectrum
        except:
            self.logger.exception("Unable to set spectrum")
            self.mode = Mode.ERROR
            self.error = Error.UNKNOWN
    

    def set_intensity(self, intensity):
        """ Set light intensity. """
        try:
            self.intensity = intensity
        except:
            self.logger.exception("Unable to set intensity")
            self.mode = Mode.ERROR
            self.error = Error.UNKNOWN

    def shutdown(self):
        """ Shutdown light panel. """
        self.set_intensity(0) # Turn off