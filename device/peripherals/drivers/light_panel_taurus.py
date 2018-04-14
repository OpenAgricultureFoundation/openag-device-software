# Import python modules
import logging, time, threading

# Import peripheral parent class
from device.peripherals.classes.peripheral import Peripheral

# Import device comms
from device.comms.i2c import I2C

# Import device modes and errors
from device.utilities.modes import Modes
from device.utilities.errors import Errors


class LightPanelTaurus(Peripheral):
    """ A light panel with six independently controlled channels that can 
    create the Taurus light spectrum. """

    # Initialize sensor parameters
    _spectrum = None
    _intensity = None

    # Initialize health metrics
    _health = None
    _minimum_health = 80.0
    _missed_readings = 0
    _readings_count = 0
    _readings_per_health_update = 20

    # TODO: put this in setup/config files
    pseudo_sensor_enabled = True

    @property
    def health(self):
        """ Gets health value. """
        return self._health


    @health.setter
    def health(self, value):
        """ Safely updates health in device state each time 
            it is changed. """
        self._health = value
        self.logger.debug("Health: {}".format(value))
        with threading.Lock():
            self.report_health(self._health)


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


    def __init__(self, *args, **kwargs):
        """ Instantiates actuator. Instantiates parent class, initializes i2c 
            mux parameters, and initializes actuator variable names. """

        # Instantiate parent class
        super().__init__(*args, **kwargs)

        # Initialize i2c mux parameters
        self.parameters = self.config["parameters"]
        self.bus = int(self.parameters["communication"]["bus"])
        self.mux = int(self.parameters["communication"]["mux"], 16)
        self.channel = int(self.parameters["communication"]["channel"])
        self.address = int(self.parameters["communication"]["address"], 16)

        # Initialize I2C communication if sensor not simulated
        if not self.simulate:
            self.logger.info("Initializing i2c bus={}, mux=0x{:02X}, channel={}, address=0x{:02X}".format(
                self.bus, self.mux, self.channel, self.address))
            self.i2c = I2C(bus=self.bus, mux=self.mux, channel=self.channel, address=self.address)

        # Initialize sensor variable names
        self.intensity_name = self.parameters["variables"]["actuator"]["intensity"]
        self.spectrum_name = self.parameters["variables"]["actuator"]["spectrum"]
        # TODO: clean up concept of a direct actuation

    def initialize(self):
        """ Initializes sensor. Performs initial health check.
            Finishes within 200ms.  """

        # Initialize sensor
        self.logger.debug("Initializing sensor")

        # Initialize reported values
        self.spectrum = None
        self.intensity = None
        self.health = 100

        # Check if simulating actuator
        # TODO: remove this once we setup a controller
        if self.simulate:
            self.intensity = 77.7
            self.specturm = [20, 20, 20, 20, 10, 10]
            self.health = 100

        # Perform initial health check
        self.perform_initial_health_check()


    def perform_initial_health_check(self):
        """ Performs initial health check. Finishes within 200ms. """
        try:
            # Do something
            self.logger.info("Passed initial health check")
        except Exception:
            self.logger.exception("Failed initial health check")
            self.error = Errors.FAILED_HEALTH_CHECK
            self.mode = Modes.ERROR

    def setup(self):
        """ Sets up actuator. Useful for actuators with warm up times >200ms """
        self.logger.debug("Setting up actuator")


    def update(self):
        """ Updates actuator. """

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


    def set_spectrum(self, spectrum):
        """ Set light spectrum. """
        try:
            self.spectrum = spectrum
        except:
            self.logger.exception("Unable to set spectrum")
            self._missed_readings += 1

        self.update_health()
    

    def set_intensity(self, intensity):
        """ Set light intensity. """
        try:
            self.intensity = intensity
        except:
            self.logger.exception("Unable to set intensity")
            self._missed_readings += 1

        self.update_health()


    def update_health(self):
        """ Updates sensor health. """

        # Increment readings count
        self._readings_count += 1

        # Update health after specified number of readings
        if self._readings_count == self._readings_per_health_update:
            good_readings = self._readings_per_health_update - self._missed_readings
            health = float(good_readings) / self._readings_per_health_update * 100
            self.health = int(health)

            # Check health is satisfactory
            if self.health < self._minimum_health:
                self.logger.warning("Unacceptable sensor health")

                # Set error
                self.error = Errors.FAILED_HEALTH_CHECK

                # Transition to error mode
                self.mode = Modes.ERROR


    def shutdown(self):
        """ Shuts down sensor. """

        # Clear reported values
        self.clear_desired_values()

        # Set sensor health
        self.health = 100


    def clear_desired_values(self):
        self.set_intensity(0)
        self.set_spectrum(None)
