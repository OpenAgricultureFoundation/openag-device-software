# Import python modules
import logging, time, threading

# Import peripheral parent class
from device.peripherals.classes.peripheral import Peripheral

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.errors import Errors

# Import device comms
from device.comms.i2c import I2C


class Atlas(Peripheral):
    """ Parent class for atlas devices. """

    # Initialize atlas parameters
    _sleep = False


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


    def process_command(self, command_string, processing_seconds, 
            num_response_bytes=31, read_retry=True, read_response=True):
        """ Sends command string to device, waits for processing seconds, then
            tries to read num response bytes with optional retry if device
            returns a `still processing` response code. Read retry is enabled 
            by default. Returns response string on success or raises exception 
            on error. """

        # Send command to device
        self.logger.debug("Sending command `{}`".format(command_string))
        with threading.Lock():
            byte_array = bytearray(command_string + "\00", 'utf8')
            self.i2c.write_raw(byte_array)

        # If read enabled, read response with optional retry
        if read_response:   
            return self.read_response(processing_seconds, num_response_bytes, retry=read_retry)
        

    def read_response(self, processing_seconds, num_response_bytes, retry=True):
        """ Reads response from from device. Waits processing seconds then 
            tries to read num response bytes with optional retry. Returns 
            response string on success or raises exception on error. """
        

        # Give device time to process
        self.logger.debug("Waiting for {} seconds".format(processing_seconds))
        time.sleep(processing_seconds)

        # Read device data and parse response code
        self.logger.debug("Reading response")
        with threading.Lock():
            data = self.i2c.read(num_response_bytes) 
        response_code = int(data[0])

        # Check command success
        if response_code == 1: # Successful response
            response_message = data[1:].decode('utf-8').strip("\x00")
            self.logger.debug("Response:`{}`".format(response_message))
            return response_message
        elif response_code == 2: # Invalid syntax
            raise SyntaxError("Invalid command string syntax")
        elif response_code == 254: # Device still processing, not ready yet
            if retry == True:
                # Try to read one more time
                self.logger.warning("Sensor did not finish processing in allotted time, retrying read")
                self.read_response(processing_seconds, num_response_bytes, retry=False)
            else:
                raise Exception("Device did not process request in time")
        elif response_code == 255: # Device has no data to send
            if retry == True:
                # Try to read one more time
                self.logger.warning("Sensor reported no data to read, retrying read")
                self.read_response(processing_seconds, num_response_bytes, retry=False)
            else:
                raise Exception("Device has no data to send")
            

    def perform_initial_health_check(self):
        """ Performs initial health check by reading device status. """
        self.logger.info("Performing initial health check")

        if self.simulate:
            self.logger.info("Simulating initial health check")
            return

        try:
            if self.status != None:
                self.logger.debug("Status not none!")
            else:
                failed_health_check = True
            self.logger.info("Passed initial health check")
        except Exception:
            self.logger.exception("Failed initial health check")
            self.error = Errors.FAILED_HEALTH_CHECK
            self.mode = Modes.ERROR


    @property
    def info(self):
        """ Queries device for info. """
        response_message = self.process_command("i", processing_seconds=0.3)
        if response_message != None:
            command, device, firmware_version = response_message.split(",")
            info = {
                "device": device,
                "firmware_version": firmware_version
            }
            return info
        else:
            return None


    @property
    def status(self):
        """ Queries device for status. """

        # Process status command
        response_message = self.process_command("Status", processing_seconds=0.3)

        # Handle none case
        if response_message == None:
            return

        # Parse response message
        command, code, voltage = response_message.split(",")
        self.logger.debug("Current voltage: {}V".format(voltage))

        # Break out restart code
        if code == "P":
            prev_restart_reason = "Powered off"
            self.logger.debug("Device previous restart due to powered off")
        elif code == "S":
            prev_restart_reason = "Software reset"
            self.logger.debug("Device previous restart due to software reset")
        elif code == "B":
            prev_restart_reason = "Browned out"
            self.logger.critical("Device browned out on previous restart")
        elif code == "W":
            prev_restart_reason = "Watchdog"
            self.logger.debug("Device previous restart due to watchdog")
        elif code == "U":
            self.prev_restart_reason = "Unknown"
            self.logger.warning("Device previous restart due to unknown")

        # Build status dict and return
        status = {
            "prev_restart_reason": prev_restart_reason,
            "voltage": voltage
        }
        return status


    @property
    def protocol_lock(self):
        """ Gets protocol lock state from device. """
        response_message = self.process_command("Plock,?", processing_seconds=0.3)
        if response_message != None:
            command, value = response_message.split(",")
            return bool(int(value))
        else:
            return None


    @protocol_lock.setter
    def protocol_lock(self, value):
        """ Sets device protocol lock state. """ 
        if value:  
            self.process_command("Plock,1", processing_seconds=0.3)
        else:
            self.process_command("Plock,0", processing_seconds=0.3)


    @property
    def led(self):
        """ Gets LED state from device. """
        response_message = self.process_command("L,?", processing_seconds=0.3)
        if response_message != None:
            command, value = response_message.split(",")
            return bool(int(value))
        else:
            return None


    @led.setter
    def led(self, value):
        """ Sets device LED state. """ 
        if value:  
            self.process_command("L,1", processing_seconds=0.3)
        else:
            self.process_command("L,0", processing_seconds=0.3)


    @property
    def sleep(self):
        """ Sleep property placeholder. """
        return None


    @sleep.setter
    def sleep(self, value):
        """ Sets device into sleep mode. Note: device wakes up by sending
            any command to it. """ 
        if value:  
            self.process_command("Sleep", processing_seconds=0.3, read_response=False)
        else:
            self.logger.debug("No need to set sleep=False, sending any command"
                " to device will wake it up.")
