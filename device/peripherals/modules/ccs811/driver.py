# Import standard python modules
import time
from typing import NamedTuple, Optional, Tuple

# Import device comms
from device.comms.i2c import I2C

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error
from device.utilities import bitwise



class CCS811Driver:
    """ Driver for atlas ccs811 co2 sensor. """

    # Initialize variable properties
    _min_carbon_dioxide = 10 # ppm
    _max_carbon_dioxide = 2000 # ppm IS THIS RIGHT?


    def __init__(self, name: str, bus: int, address: int, mux: Optional[int] = None, 
            channel: Optional[int] = None, simulate: bool = False) -> None:
        """ Initializes sht25 driver. """

        # Initialize parameters
        self.simulate = simulate

        # Initialize logger
        self.logger = Logger(
            name = "Driver({})".format(name),
            dunder_name = __name__,
        )

        # Initialize I2C
        self.i2c = I2C(
            name = name,
            bus = bus,
            address = address,
            mux = mux,
            channel = channel,
            simulate = simulate,
        )


    def read_carbon_dioxide(self) -> Tuple[Optional[float], Error]:
        """ Reads carbon dioxide value from sensor hardware. """
        self.logger.debug("Reading carbon dioxide")
        
        # Send read temperature command (no-hold master)
        error = self.i2c.write([0xF3])

        # Check for errors
        if error.exists():
            error.report("Driver unable to read temperature")
            self.logger.error(error.summary())
            return None, error
            
        # Wait for sensor to process, see datasheet Table 7
        # SHT25 is 12-bit so max temperature processing time is 22ms
        time.sleep(0.22)

        # Read sensor data
        bytes_, error = self.i2c.read(2)

        # Check for errors
        if error.exists():
            error.report("Driver unable to read temperature")
            self.logger.error(error.summary())
            return None, error

        # Convert temperature data and set significant figures
        msb, lsb = bytes_
        raw = msb * 256 + lsb
        temperature = -46.85 + ((raw * 175.72) / 65536.0)
        temperature = float("{:.0f}".format(temperature))

        

        # Verify temperature value within valid range
        if carbon_dioxide > self._min_carbon_dioxide and carbon_dioxide < self._min_carbon_dioxide:
            self.logger.warning("Carbon dioxide outside of valid range")
            carbon_dioxide = None

        # Successfully read temperature!
        self.logger.debug("Carbon Dioxide: {} ppm".format(carbon_dioxide))
        return carbon_dioxide, Error(None)
