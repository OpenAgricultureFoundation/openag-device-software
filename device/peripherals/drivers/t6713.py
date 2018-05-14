# Import python modules
import logging, time, threading

# Import dataclasses
from typing import NamedTuple

# Import peripheral parent class
from device.peripherals.classes.peripheral import Peripheral

# Import device modes and errors
from device.utilities.modes import Modes
from device.utilities.errors import Errors


class T6713(Peripheral):
    """ Co2 sensor. """

    # Initialize sensor parameters
    _co2 = None

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

        # Initialize sensor variable names
        self.co2_name = self.parameters["variables"]["sensor"]["co2_ppm"]


    def initialize(self):
        """ Initializes sensor. Performs initial health check.
            Finishes within 200ms.  """

        # Initialize sensor
        self.logger.debug("Initializing sensor")

        # Initialize reported values
        self.co2 = None
        self.health = 100

        # Perform initial health check
        self.check_health()
            

    def setup(self):
        """ Sets up sensor. Useful for sensors with warm up times >200ms """
        self.logger.debug("Setting up sensor")

        # Disable ABC auto-calibration logic
        try:
            self.disable_abc_logic()
        except:
            self.error = "Failed disable abc logic"
            self.logger.exception(self.error)
            self.mode = Modes.ERROR
            return

        # Wait for sensor to finish warming by polling status register
        self.logger.debug("Sensor is warming up")
        while True:
            status = self.read_status()
            if not status.warm_up_mode:
                self.logger.debug("Sensor finished warming up")
                break


    def update(self):
        """ Updates sensor. """
        self.update_co2()
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
            self.error = "Sensor reset failed"
            self.logger.exception(self.error)
            self.mode = Modes.ERROR


    def shutdown(self):
        """ Shuts down sensor. """
        self.logger.info("Shutting down sensor")
        self.clear_reported_values()
        self.logger.debug("Successfully shutdown sensor")


############################# Main Helper Functions ###########################


    def check_health(self):
        """ Checks health by reading status from sensor hardware and verifying 
            sensor not in error condition. """

        # Read status from sensor hardware
        try:
            status = self.read_status()
            if status.error_condition:
                raise ValueError("Sensor hardware has error condition")
        except:
            self.error = "Failed health check"
            self.logger.exception(self.error)
            self.mode = Modes.ERROR
            return

        # Sensor is healthy!
        self.logger.info("Passed health check")
            

    def update_co2(self):
        """ Updates sensor co2. """
        self.logger.debug("Updating co2")
        try:
            self.co2 = self.read_co2()
        except:
            self.logger.exception("Unable to update co2, bad reading")
            self._missed_readings += 1


    def clear_reported_values(self):
        """ Clears reported values. """
        self.co2 = None


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


    def read_co2(self):
        """ Reads co2 value from sensor hardware. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating reading co2 value from hardware")
            co2 = 440
            self.logger.debug("co2 = {}".format(co2))
            return co2
       
        # Sensor is not simulated
        self.logger.debug("Reading co2 value from hardware")

        # Send read command
        with threading.Lock():
            self.i2c.write([0x04, 0x13, 0x8b, 0x00, 0x01]) 
        
        # Wait for sensor to process
        time.sleep(0.1) 

        # Read sensor data
        with threading.Lock():
            _, _, msb, lsb = self.i2c.read(4) 

        # Convert co2 data
        co2 = float(msb*256 + lsb)

        # Set significant figures
        co2 = round(co2, 0)

        # Return co2 value
        self.logger.debug("co2 = {}".format(co2))
        return co2


    def read_status(self):
        """ Reads status from sensor hardware. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating reading status from sensor hardware")
            status = Status(
                error_condition = 0,
                flash_error = 0,
                calibration_error = 0,
                rs232 = 0,
                rs485 = 0,
                i2c = 0,
                warm_up_mode = 0,
                single_point_calibration = 0,
            )
            self.logger.debug("status = {}".format(status))
            return status

        # Sensor is not simulated
        self.logger.debug("Reading status from sensor hardware")

        try:
            # Send read status command
            with threading.Lock():
                self.i2c.write([0x04, 0x13, 0x8a, 0x00, 0x01]) 
            
            # Wait for sensor to process
            time.sleep(0.1) 

            # Read sensor data
            with threading.Lock():
                _, _, status_msb, status_lsb = i2c.read(4) 

            # Parse status bytes
            status = Status(
                error_condition = self.get_bit_from_byte(0, status_lsb),
                flash_error = self.get_bit_from_byte(1, status_lsb),
                calibration_error = self.get_bit_from_byte(2, status_lsb),
                rs232 = self.get_bit_from_byte(0, status_msb),
                rs485 = self.get_bit_from_byte(1, status_msb),
                i2c = self.get_bit_from_byte(2, status_msb),
                warm_up_mode = self.get_bit_from_byte(3, status_msb),
                single_point_calibration = self.get_bit_from_byte(7, status_msb),
            )

            # Return status
            self.logger.debug("status = {}".format(status))
            return status

        except:
            self.logger.exception("Unable to readBad status reading")
            self._missed_readings += 1


    def enable_abc_logic(self):
        """ Enables ABC logic on sensor hardware. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating enabling abc logic on sensor hardware")
            return

        # Sensor is not simulated
        self.logger.debug("Enabling abc logic on sensor hardware")

        # Send enable command
        with threading.Lock():
            self.i2c.write([0x05, 0x03, 0xEE, 0xFF, 0x00]) 


    def disable_abc_logic(self):
        """ Disables ABC logic on sensor hardware. """

        # Check for simulated sensor
        if self.simulate:
            self.logger.debug("Simulating disabling abc logic on sensor hardware")
            return

        # Sensor is not simulated
        self.logger.debug("Disable abc logic on sensor hardware")

        # Send enable command
        with threading.Lock():
            self.i2c.write([0x05, 0x03, 0xEE, 0x00, 0x00]) 
        

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
            self.i2c.write([0x05, 0x03, 0xE8, 0xFF, 0x00])


########################## Setter & Getter Functions ##########################


    @property
    def co2(self):
        """ Gets co2 value. """
        return self._co2


    @co2.setter
    def co2(self, value):
        """ Safely updates co2 in environment state each time
            it is changed. """   
        self._co2 = value
        self.report_environment_sensor_value(self.name, self.co2_name, value)
        self.report_peripheral_sensor_value(self.co2_name, value)


############################### Data Classes ##################################


class Status(NamedTuple):
    error_condition: bool
    flash_error: bool
    calibration_error: bool
    rs232: bool
    rs485: bool
    i2c: bool
    warm_up_mode: bool
    single_point_calibration: bool
