# Import standard python modules
import time
from typing import NamedTuple, Optional, Tuple

# Import device comms
from device.comms.i2c import I2C

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error
from device.utilities import bitwise


class StatusRegister(NamedTuple):
    firmware_mode: int
    app_valid: bool
    data_ready: bool
    error: bool


class ErrorRegister(NamedTuple):
    message_invalid: bool
    read_register_invalid: bool
    measurement_mode_invalid: bool
    max_resistance: bool
    heater_fault: bool
    heater_supply: bool


class CCS811Driver:
    """ Driver for atlas ccs811 carbon dioxide and total volatile organic compounds sensor. """

    # Initialize variable properties
    _min_co2 = 400.0 # ppm
    _max_co2 = 8192.0 # ppm
    _min_tvoc = 0.0 # ppb
    _max_tvoc = 1187.0 # ppb


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


    def read_hardware_id(self) -> Tuple[Optional[int], Error]:
        """ Reads hardware ID from sensor. """
        self.logger.debug("Reading hardware ID")

        # Read register
        byte, error = self.i2c.read_register(0x20):

        # Check for errors
        if error.exists():
            error.report("Unable to read hardware id")
            self.logger.error(error.summary())
            return None, error

        # Return hardware id
        return byte, Error(None)


    def read_status_register(self) -> Tuple[Optional[StatusRegister], Error]:
        """ Reads status of sensor. """
        self.logger.debug("Reading status register")
        
        # Read byte from status register
        byte = self.i2c.read_register([0x00])

        # Check for errors
        if error.exists():
            error.report("Driver unable to read status register")
            self.logger.error(error.summary())
            return None, error

        # Parse status register byte
        status_register =  StatusRegister(
            firmware_mode = bitwise.get_bit_from_byte(7, byte),
            app_valid = bool(bitwise.get_bit_from_byte(4, byte)),
            data_ready = bool(bitwise.get_bit_from_byte(3, byte)),
            error = bool(bitwise.get_bit_from_byte(0, byte)),
        )

        # Successfully read status register!
        return status_register, Error(None)


    def read_error_register(self) -> Tuple[Optional[ErrorRegister], Error]:
        """ Reads error register. """
        self.logger.debug("Reading error register")

        # Read byte from error register
        byte = self.i2c.read_register([0x0E])

        # Check for errors
        if error.exists():
            error.report("Driver unable to read error register")
            self.logger.error(error.summary())
            return None, error

        # Parse error register byte
        error_register = ErrorRegister(
            message_invalid = bool(bitwise.get_bit_from_byte(0, byte)),
            read_register_invalid = bool(bitwise.get_bit_from_byte(1, byte)),
            measurement_mode_invalid = bool(bitwise.get_bit_from_byte(2, byte)),
            max_resistance = bool(bitwise.get_bit_from_byte(3, byte)),
            heater_fault = bool(bitwise.get_bit_from_byte(4, byte)),
            heater_supply = bool(bitwise.get_bit_from_byte(5, byte)),
        )

        # Successfully read error!
        return error_register, Error(None)


    def write_measurement_mode(self, drive_mode: int, enable_data_ready_interrupt: bool, 
            enable_threshold_interrupt: bool) -> Error: 
        """ Writes measurement mode to the sensor. """
        self.logger.debug("Writing measurement mode")

        # Initialize bits
        bits = {7: 0, 1:0, 0:0}

        # Set drive mode
        if drive_mode == 0:
            bits.update({6:0, 5:0, 4:0})
        elif drive_mode == 1:
            bits.update({6:0, 5:0, 4:1})
        elif drive_mode == 2:
            bits.update({6:0, 5:1, 4:0})
        elif drive_mode == 3:
            bits.update({6:0, 5:1, 4:1})
        elif drive_mode == 4:
            bits.update({6:1, 5:0, 4:0})
        else:
            error = Error("Driver unable to write measurement mode, invalid drive mode")
            self.logger.error(error.latest())
            return error

        # Set data ready interrupt
        bits.update({3: int(enable_data_ready_interrupt)})

        # Set threshold interrupt
        bits.update({2: int(enable_data_ready_interrupt)})

        self.logger.error("bits = {}".format(bits))

        # Convert bits to byte
        byte = bitwise.bits_to_byte(bits)

        self.logger.error("byte = {:02X}".format(byte))

        # Write mode to sensor
        error = self.i2c.write([0x01, byte])

        # Check for errors
        if error.exists():
            error.report("Unable to write measurement mode")
            self.logger.error(error.summary())
            return error

        # Successfully wrote measurement mode!
        return Error(None)


    def write_environment_data(self, temperature=None, humidity=None): 
        """ Writes compensation temperature and / or humidity to sensor. """
        self.logger.debug("Writing environment data")

        # Check valid environment values
        if temperature == None and humidity == None:
            raise ValueError("Temperature and/or humidity value required")

        # TODO: Calculate temperature bytes
        if temperature != None:
            ...
        else:
            temperature_msb = 0x64
            temperature_lsb = 0x00

        # TODO: Calculate humidity bytes
        if humidity != None:
            ...
        else:
            humidity_msb = 0x64
            humidity_lsb = 0x00

        # Write environment data
        error = self.i2c.write([0x05, humidity_msb, humidity_lsb, temperature_msb, temperature_lsb])

        # Check for errors
        if error.exists():
            error.report("Unable to write environment data")
            self.logger.error(error.summary())
            return error

        # Successfully wrote environment data!
        return Error(None)


    def read_algorithm_data(self) -> Tuple[Optional[float], Optional[float], Error]:
        """ Reads algorighm data from sensor hardware. """
        self.logger.debug("Reading carbon dioxide")

        # Read status register
        status, error = self.read_status()

        # Check for errors
        if error.exists():
            error.report("Unable to read sensor data")
            self.logger.error(error.summary())
            return None, None, error

        # Check if data is ready
        if not status.data_ready:
            error = Error("Driver unable to read sensor data, data not ready")
            self.logger.error(error)
            return None, None, error

        # Request data
        error = self.i2c.write([0x02])

        # Check for errors
        if error.exists():
            error.report("Unable to read sensor data")
            self.logger.error(error.summary())
            return None, None, error

        # Read data
        bytes_, error = self.i2c.read(4)

        # Check for errors
        if error.exists():
            error.report("Unable to read sensor data")
            self.logger.error(error.summary())
            return None, None, error

        # Parse data bytes
        co2 = float(bytes_[0]*255 + bytes_[1])
        tvoc = float(bytes_[2]*255 + bytes_[3])

        # Verify co2 value within valid range
        if co2 > self._min_co2 and co2 < self._min_co2:
            self.logger.warning("Carbon dioxide outside of valid range")
            co2 = None

        # Verify tvos within valid range
        if tvoc > self._min_tvoc and tvoc < self._min_tvoc:
            self.logger.warning("Total volatile organic compounds outside of valid range")
            tvoc = None

        # Successfully read sensor data!
        self.logger.debug("Carbon Dioxide: {} ppm".format(co2))
        self.logger.debug("Total Volatile Organic Compounds: {} ppb".format(tvoc))
        return co2, tvoc, Error(None)


    def read_raw_data(self) -> Error:
        """ Reads raw data from sensor. """
        ...


    def read_ntc(self) -> Error:
        """ Read value of NTC. Can be used to calculate temperature. """
        ...


    def reset(self) -> Error:
        """ Resets sensor and places into boot mode. """
        ...




