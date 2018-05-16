# Import python modules
import logging, time, threading

# Import peripheral parent class
from device.peripherals.classes.peripheral import Peripheral

# Import device modes and errors
from device.utilities.modes import Modes
from device.utilities.errors import Errors


class SHT25(Peripheral):
    """ Temperature and humidity sensor. """

    # Initialize sensor variable parameters
    _temperature_celcius = None
    _humidity_percent = None

    # Initialize sampling interval parameters
    _min_sampling_interval_seconds = 1
    _default_sampling_interval_seconds = 5


    def __init__(self, *args, **kwargs):
        """ Instantiates sensor. Instantiates parent class, initializes i2c 
            mux parameters, and initializes sensor variable names. """

        # Instantiate parent class
        super().__init__(*args, **kwargs)     

        # Establish i2c connection
        self.establish_i2c_connection()

        # Get sensor variable names
        self.temperature_name = self.parameters["variables"]["sensor"]["temperature_celcius"]
        self.humidity_name = self.parameters["variables"]["sensor"]["humidity_percent"]


    def initialize(self):
        """ Initializes sensor. Performs initial health check. Finishes within 200ms.  """

        # Initialize sensor
        self.logger.debug("Initializing sensor")

        # Initialize reported values
        self.temperature_celcius = None
        self.humidity_percent = None
        self.health = 100

        # Perform initial health check
        self.check_health()


    def setup(self):
        """ Sets up sensor. Useful for sensors with startup processes >200ms. 
            Don't forget to check for events if this is just waiting for a 
            sensor to warmup. """
        self.logger.debug("No sensor setup is required")


    def update(self):
        """ Updates sensor. """
        self.update_temperature_celcius()
        self.update_humidity_percent()
        self.update_health()


    def reset(self): 
        """ Resets sensor. """
        self.logger.info("Resetting sensor")

        # Clear reported values
        self.clear_reported_values()

        # Send soft reset command to sensor hardware
        try:
            self.initiate_soft_reset()
            self.logger.debug("Successfully reset sensor")
        except:
            self.logger.exception("Sensor reset failed")
            self.mode = Modes.ERROR


    def shutdown(self):
        """ Shuts down sensor. """
        self.logger.info("Shutting down sensor")
        self.clear_reported_values()
        self.logger.debug("Successfully shutdown sensor")


############################# Main Helper Functions ###########################


    def check_health(self):
        """ Checks health by reading user register from sensor hardware and 
            verifying resolutions"""
        try:
            register, _, _, _ = self.read_user_register()
            if register != 0:
                raise ValueError("Unexpected sensor resolution")
            self.logger.info("Passed health check")
        except Exception:
            self.error = "Failed health check"
            self.logger.exception(self.error)
            self.mode = Modes.ERROR


    def update_temperature_celcius(self):
        """ Updates sensor temperature_celcius. """
        self.logger.debug("Updating temperature")
        try:
            # Update temperature_celcius in shared state
            self.temperature_celcius = self.read_temperature_celcius()
        except:
            self.logger.exception("Unable to update temperature, bad reading")
            self._missed_readings += 1


    def update_humidity_percent(self):
        """ Updates sensor humidity_percent. """
        self.logger.debug("Updating humidity")
        try:
            # Update temperature_celcius in shared state
            self.humidity_percent = self.read_humidity_percent()
        except:
            self.logger.exception("Unable to update humidity, bad reading")
            self._missed_readings += 1


    def clear_reported_values(self):
        """ Clears reported values. """
        self.temperature_celcius = None
        self.humidity_percent = None


################# Peripheral Specific Event Functions #########################

    
    def process_peripheral_specific_event(self, request_type, value):
        """ Processes and event. Gets request parameters, executes request, returns 
            response. """

        # Execute request
        if request_type == "Example Request Type":
            # self.response = self.process_example_request()
            pass
        else:
            message = "Unknown event request type!"
            self.logger.info(message)
            self.response = {"status": 400, "message": message}


############################# Hardware Interactions ###########################


    def read_temperature_celcius(self):
        """ Reads temperature value from sensor hardware. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating reading temperature value from hardware")
            temperature_celcius = 22.2
            self.logger.debug("temperature_celcius = {}".format(temperature_celcius))
            return temperature_celcius
       
        # Sensor is not simulated
        self.logger.debug("Reading temperature value from hardware")
        
        # Send read temperature command (no-hold master)
        with threading.Lock():
            self.i2c.write([0xF3])
            
        # Wait for sensor to process, see datasheet Table 7
        # SHT25 is 12-bit so max temperature processing time is 22ms
        time.sleep(0.22)

        # Read sensor data
        with threading.Lock():
            msb, lsb = self.i2c.read(2)

        # Convert temperature data and set significant figures
        raw = msb * 256 + lsb
        temperature_celcius = -46.85 + ((raw * 175.72) / 65536.0)
        temperature_celcius = float("{:.0f}".format(temperature_celcius))

        # Return temperature value
        self.logger.debug("temperature_celcius = {}".format(temperature_celcius))
        return temperature_celcius


    def read_humidity_percent(self):
        """ Reads humidity value from sensor hardware. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating reading humidity value from hardware")
            humidity_percent = 33.3
            self.logger.debug("humidity_percent = {}".format(humidity_percent))
            return humidity_percent

        # Sensor is not simulated
        self.logger.debug("Reading humidity value from hardware")

        # Send read humidity command (no-hold master)
        with threading.Lock():
            self.i2c.write([0xF5])

        # Wait for sensor to process, see datasheet Table 7
        # SHT25 is 12-bit so max humidity processing time is 29ms
        time.sleep(0.29)

        # Read sensor
        with threading.Lock():
            msb, lsb = self.i2c.read(2) # Read sensor data

        # Convert humidity data and set significant figures
        raw = msb * 256 + lsb
        humidity_percent = -6 + ((raw * 125.0) / 65536.0)
        humidity_percent = float("{:.0f}".format(humidity_percent))
        
        # Return humidity value
        self.logger.debug("humidity_percent = {}".format(humidity_percent))
        return humidity_percent


    def read_user_register(self): 
        """ Reads user register from sensor hardware. """

        # Check if sensor is simulated
        if self.simulate:
            self.logger.info("Simulating reading user register")
            resolution = 0
            end_of_battery = 0
            heater_enabled = 0
            reload_disabled = 1
            self.logger.debug("resolution={}, end_of_battery={}, heater_enabled={}, reload_disabled={}".format(
                resolution, end_of_battery, heater_enabled, reload_disabled))
            return resolution, end_of_battery, heater_enabled, reload_disabled

        # Sensor is not simulated
        self.logger.debug("Reading user register")

        # Get register content
        with threading.Lock():
            self.i2c.write([0xE7])
            register_content = self.i2c.read(1)[0]

        # Parse register content
        self.logger.debug("register_content = 0x{:02X}".format(register_content))
        resolution_msb = self.get_bit_from_byte(bit=7, byte=register_content)
        resolution_lsb = self.get_bit_from_byte(bit=0, byte=register_content)
        resolution = resolution_msb << 1 + resolution_lsb
        end_of_battery = self.get_bit_from_byte(bit=6, byte=register_content)
        heater_enabled = self.get_bit_from_byte(bit=2, byte=register_content)
        reload_disabled = self.get_bit_from_byte(bit=1, byte=register_content)

        # Return parsed register content
        self.logger.debug("resolution={}, end_of_battery={}, heater_enabled={}, reload_disabled={}".format(
            resolution, end_of_battery, heater_enabled, reload_disabled))
        return resolution, end_of_battery, heater_enabled, reload_disabled


    def initiate_soft_reset(self):
        """ Initiates soft reset on sensor hardware. """

        # Check if sensor is simulated
        if self.simulate:
            self.logger.info("Simulating initiating soft reset")
            return

        # Sensor is not simulated
        self.logger.info("Initiating soft reset")

        # Trigger reset
        with threading.Lock():
            self.i2c.write([0xFE])


########################## Setter & Getter Functions ##########################


    @property
    def temperature_celcius(self):
        """ Gets temperature_celcius value. """
        return self._temperature_celcius


    @temperature_celcius.setter
    def temperature_celcius(self, value):
        """ Safely updates temperature_celcius in environment state each time
            it is changed. """   
        self._temperature_celcius = value
        self.report_environment_sensor_value(self.name, self.temperature_name, value)
        self.report_peripheral_sensor_value(self.temperature_name, value)


    @property
    def humidity_percent(self):
        """ Gets humidity_percent value. """
        return self._humidity_percent


    @humidity_percent.setter
    def humidity_percent(self, value):
        """ Safely updates humidity_percent in environment state each time 
            it is changed. """
        self._humidity_percent = value
        self.report_environment_sensor_value(self.name, self.humidity_name, value)
        self.report_peripheral_sensor_value(self.humidity_name, value)