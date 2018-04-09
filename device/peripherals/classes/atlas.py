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
