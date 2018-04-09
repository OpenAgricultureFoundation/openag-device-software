# Import python modules
import logging, time, threading

# Import peripheral parent class
from device.peripherals.classes.peripheral import Peripheral

# Import device comms
from device.comms.i2c import I2C

# Import device modes and errors
from device.utilities.mode import Mode
from device.utilities.error import Error


class Atlas(Peripheral):
    """ Parent class for atlas devices. """

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


    def read_value(self):
        """ Reads sensor value. Sends request to read sensor, waits for sensor
            to process then reads and returns read value. """
        try:
            # Send read command
            with threading.Lock():
                bytes = bytearray("R\00", 'utf8') # Create byte array
                self.i2c.write_raw(bytes) # Send get ec command
            
            # Wait for sensor to process
            time.sleep(0.9) 

            # Read sensor data
            with threading.Lock():
                data = self.i2c.read(8) 
                if len(data) != 8:
                    self.logger.critial("Requested 8 bytes but only received {}".format(len(data)))

            # Convert status data
            status = data[0] 

            # Convert value data and return
            return float(data[1:].decode('utf-8').strip("\x00"))
        
        except:
            self.logger.exception("Bad reading")
            self._missed_readings += 1


    def process_command(self, command_string, processing_seconds, num_response_bytes=31):
        """ Read a string from an atlas device. """

        # Send command to device
        with threading.Lock():
            byte_array = bytearray(command_string + "\00", 'utf8')
            self.i2c.write_raw(byte_array)
        
        # Give device time to process
        time.sleep(processing_seconds)

        # Read device data
        with threading.Lock():
            data = self.i2c.read(num_response_bytes) 

        # Check command success
        response_code = int(data[0])
        if response_code == 2:
            raise SyntaxError("Invalid command string syntax")
        elif response_code == 1:
            response_message = data[1:].decode('utf-8').strip("\x00")
            self.logger.debug("Response:`{}`".format(response_message))


        return response_message


    @property
    def info(self):
        """ Queries device for info. """
        response_message = self.process_command("i", 0.3)
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
        response_message = self.process_command("Status", 0.3)

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
        response_message = self.process_command("Plock,?", 0.3)
        if response_message != None:
            command, value = response_message.split(",")
            return bool(int(value))
        else:
            return None


    @protocol_lock.setter
    def protocol_lock(self, value):
        """ Sets device protocol lock state. """ 
        if value:  
            self.process_command("Plock,1", 0.3)
        else:
            self.process_command("Plock,0", 0.3)


    @property
    def led(self):
        """ Gets LED state from device. """
        response_message = self.process_command("L,?", 0.3)
        if response_message != None:
            command, value = response_message.split(",")
            return bool(int(value))
        else:
            return None


    @led.setter
    def led(self, value):
        """ Sets device LED state. """ 
        if value:  
            self.process_command("L,1", 0.3)
        else:
            self.process_command("L,0", 0.3)



