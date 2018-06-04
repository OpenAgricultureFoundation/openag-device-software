# Import standard python modules
import time, threading
from typing import NamedTuple, Optional, Tuple

# Import device comms
from device.comms.i2c import I2C

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error
from device.utilities import bitwise


class Status (NamedTuple):
    """ Data class for parsed status. """
    error_condition: bool
    flash_error: bool
    calibration_error: bool
    rs232: bool
    rs485: bool
    i2c: bool
    warm_up_mode: bool
    single_point_calibration: bool


class T6713Driver:
    """ Driver for atlas t6713 carbon dioxide sensor. """


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
        self.logger.debug("Reading carbon dioxide value from hardware")

        # TODO: Convert this to a block read in i2c comm
        with threading.Lock():

            # Send read carbon dioxide command
            error = self.i2c.write([0x04, 0x13, 0x8b, 0x00, 0x01]) 

            # Check for errors
            if error.exists():
                error.report("Driver unable to read carbon dioxide")
                return None, error

            # Read sensor data
            bytes_, error = self.i2c.read(4, disable_mux=True) # don't re-set mux channel
        
        # Check for errors
        if error.exists():
            error.report("Driver unable to read carbon dioxide")
            return None, error

        # Convert temperature data and set significant figures
        _, _, msb, lsb = bytes_
        carbon_dioxide = float(msb*256 + lsb)
        carbon_dioxide = round(carbon_dioxide, 0)

        # Successfully read carbon dioxide!
        self.logger.debug("Co2: {} ppm".format(carbon_dioxide))
        return carbon_dioxide, Error(None)


    def read_status(self) -> Tuple[Optional[Status], Error]:
        """ Reads status from sensor hardware. """
        self.logger.debug("Reading status from sensor hardware")

        time.sleep(0.3)

        # Send command
        error = self.i2c.write([0x04, 0x13, 0x8a, 0x00, 0x01]) 

        # Check for errors
        if error.exists():
            error.report("Driver unable to read status")
            return None, error

        # Give sensor time to process
        time.sleep(0.2)

        # Read status data
        bytes_, error = self.i2c.read(4, disable_mux=True)

        # Check for errors
        if error.exists():
            error.report("Driver unable to read status")
            return None, error    

        # Parse status bytes
        _, _, status_msb, status_lsb = bytes_
        status = Status(
            error_condition = bool(bitwise.get_bit_from_byte(0, status_lsb)),
            flash_error = bool(bitwise.get_bit_from_byte(1, status_lsb)),
            calibration_error = bool(bitwise.get_bit_from_byte(2, status_lsb)),
            rs232 = bool(bitwise.get_bit_from_byte(0, status_msb)),
            rs485 = bool(bitwise.get_bit_from_byte(1, status_msb)),
            i2c = bool(bitwise.get_bit_from_byte(2, status_msb)),
            warm_up_mode = bool(bitwise.get_bit_from_byte(3, status_msb)),
            single_point_calibration = bool(bitwise.get_bit_from_byte(7, status_msb)),
        )

        # Successfully read status!
        self.logger.debug("Status: {}".format(status))
        return status, Error(None)


    def enable_abc_logic(self):
        """ Enables ABC logic on sensor hardware. """
        self.logger.debug("Enabling abc logic on sensor hardware")

        # Send command
        error = self.i2c.write([0x05, 0x03, 0xEE, 0xFF, 0x00]) 

        # Check for errors
        if error.exists():
            error.report("Driver unable to enable abc logic")
            return error

        # Successfully enabled abc logic!
        return Error(None)


    def disable_abc_logic(self):
        """ Disables ABC logic on sensor hardware. """
        self.logger.debug("Disabling abc logic on sensor hardware")

        # Send command
        error = self.i2c.write([0x05, 0x03, 0xEE, 0x00, 0x00]) 

        # Check for errors
        if error.exists():
            error.report("Driver unable to disable abc logic")
            return error

        # Successfully disabled abc logic!
        return Error(None)
        

    def reset(self):
        """ Initiates soft reset on sensor hardware. """
        self.logger.info("Resetting")

        # Send command
        error = self.i2c.write([0x05, 0x03, 0xE8, 0xFF, 0x00])

        # Check for errors
        if error.exists():
            error.report("Driver unable to reset")
            return error

        # Successfully reset!
        return Error(None)
