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
    _spectrum_taurus = None
    _intensity_par = None

    # TODO: put this in setup/config files
    pseudo_sensor_enabled = True


    def __init__(self, *args, **kwargs):
        """ Instantiates sensor. Instantiates parent class, and initializes 
            sensor variable name. """

        # Instantiate parent class
        super().__init__(*args, **kwargs)

        # Initialize i2c mux parameters
        self.parameters = self.config["parameters"]
        self.bus = int(self.parameters["communication"]["bus"])
        self.mux = int(self.parameters["communication"]["mux"], 16) # Convert from hex string
        self.channel = int(self.parameters["communication"]["channel"])
        self.address = int(self.parameters["communication"]["address"], 16) # Convert from hex string
        
        # Initialize I2C communication if sensor not simulated
        if not self.simulate:
            self.logger.info("Initializing i2c bus={}, mux=0x{:02X}, channel={}, address=0x{:02X}".format(
                self.bus, self.mux, self.channel, self.address))
            self.i2c = I2C(bus=self.bus, mux=self.mux, channel=self.channel, address=self.address)

        # Initialize desired actuator names
        self.desired_spectrum_name = self.parameters["variables"]["actuator"]["spectrum_taurus"]
        self.desired_intensity_name = self.parameters["variables"]["actuator"]["intensity_par"]

        # Initialize reported sensor names
        self.reported_spectrum_name = self.parameters["variables"]["sensor"]["spectrum_taurus"]
        self.reported_intensity_name = self.parameters["variables"]["sensor"]["intensity_par"]

        # TODO: Load this in from device config file
        self.setup_uuid = "d0eec6ec-58de-497e-9676-45de7ae500d6"


    @property
    def spectrum_taurus(self):
        """ Gets spectrum value. """
        return self._spectrum_taurus


    @spectrum_taurus.setter
    def spectrum_taurus(self, value):
        """ Safely updates spectrum in environment object each time
            it is changed. """
        self._spectrum_taurus = value
        with threading.Lock():
            self.report_actuator_value(self.name, self.desired_spectrum_name, self.spectrum_taurus)
            if self.pseudo_sensor_enabled:
                # Report simply since data is an array of ints
                self.report_sensor_value(self.name, self.reported_spectrum_name, self.spectrum_taurus, simple=True)


    @property
    def intensity_par(self):
        """ Gets intensity value. """
        return self._intensity_par


    @intensity_par.setter
    def intensity_par(self, value):
        """ Safely updates intensity in environment object each time 
            it is changed. """
        self._intensity_par = value
        with threading.Lock():
            self.report_actuator_value(self.name, self.desired_intensity_name,  self.intensity_par)
            if self.pseudo_sensor_enabled:
                self.report_sensor_value(self.name, self.reported_intensity_name, self.intensity_par)


    def initialize(self):
        """ Initializes sensor. Performs initial health check.
            Finishes within 200ms.  """

        # Initialize sensor
        self.logger.debug("Initializing sensor")

        # Check if simulating actuator
        # TODO: remove this once we setup a controller
        if self.simulate:
            self.intensity = 77.7
            self.specturm = [20, 20, 20, 20, 10, 10]
            self.health = 100
        else:
            self.spectrum_taurus = None
            self.intensity_par = None
            self.health = 100

        # Perform initial health check
        self.perform_initial_health_check()


    def perform_initial_health_check(self):
        """ Performs initial health check by TBD...."""

        # Check for simulated sensor
        if self.simulate:
            self.logger.info("Simulating initial health check")
            return
        else:
            self.logger.info("Performing initial health check")

        # Check sensor health
        try:
            # TODO: Do something
            self.logger.debug("Passed initial health check")
        except:
            self.logger.exception("Failed initial health check")
            self.error = Errors.FAILED_HEALTH_CHECK
            self.mode = Modes.ERROR


    def setup(self):
        """ Sets up actuator. Useful for actuators with warm up times >200ms """
        
        # Check for simulated sensor
        if self.simulate:
            self.logger.info("Simulating sensor setup")
            return
        else:
            self.logger.debug("Setting up sensor")

        # Setup sensor
        try:    
            # TODO: Do something
            self.logger.debug("Successfully setup sensor")
        except:
            self.logger.exception("Sensor setup failed")
            self.mode = Modes.ERROR


    def update(self):
        """ Updates actuator. """

        # Check for new desired spectrum and update if so
        if self.desired_spectrum_name in self.state.environment["sensor"]["desired"]:
            desired_spectrum = self.state.environment["sensor"]["desired"][self.desired_spectrum_name]
            if desired_spectrum != self.spectrum_taurus:
                self.set_spectrum(desired_spectrum)

        # Check for new desired intensity and update if so
        if self.desired_intensity_name in self.state.environment["sensor"]["desired"]:
            desired_intensity = self.state.environment["sensor"]["desired"][self.desired_intensity_name]
            if desired_intensity != self.intensity_par:
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


    def shutdown(self):
        """ Shuts down sensor. """

        # Clear reported values
        self.clear_desired_values()
        self.clear_reported_values()

        # Set sensor health
        self.health = 100


    def clear_desired_values(self):
        self.set_intensity(0)
        self.set_spectrum(None)


    def clear_reported_valus(self):
        self.intensity_par = None
        self.spectrum_taurus = None


################################## Events #####################################

    def process_event(self, request):
        """ Processes and event. Gets request parameters, executes request, returns 
            response. """

        self.logger.debug("Processing event request: `{}`".format(request))

        # Get request parameters
        try:
            request_type = request["type"]
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            self.response = {"status": 400, "message": "Invalid request parameters: {}".format(e)}

        # Execute request
        if request_type == "Reset":
            self.response = self.process_reset_event(request)
        else:
            message = "Unknown event request type"
            self.logger.info(message)
            self.response = {"status": 400, "message": message}


    def process_reset_event(self, request):
        """ Processes reset event. """
        self.logger.debug("Processing reset event")
        self.mode = Modes.RESET
        response = {"status": 200, "message": "Resetting peripheral"}
        return response


    # TODO: add process_sampling_interval event with checks for min update interval
