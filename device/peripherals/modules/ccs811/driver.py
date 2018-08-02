# Import standard python modules
import time, threading
from typing import NamedTuple, Optional, Tuple

# Import device comms
from device.comms.i2c2.main import I2C
from device.comms.i2c2.mux_simulator import MuxSimulator
from device.comms.i2c2.exceptions import I2CError

# Import device utilities
from device.utilities.logger import Logger
from device.utilities import bitwise

# Import driver elements
from device.peripherals.modules.ccs811.simulator import CCS811Simulator
from device.peripherals.modules.ccs811.exceptions import *


class StatusRegister(NamedTuple):
    firmware_mode: int
    app_valid: bool
    data_ready: bool
    error: bool


class ErrorRegister(NamedTuple):
    write_register_invalid: bool
    read_register_invalid: bool
    measurement_mode_invalid: bool
    max_resistance: bool
    heater_fault: bool
    heater_supply: bool


class CCS811Driver:
    """Driver for atlas ccs811 carbon dioxide and total volatile organic compounds sensor."""

    # Initialize variable properties
    _min_co2 = 400.0  # ppm
    _max_co2 = 8192.0  # ppm
    _min_tvoc = 0.0  # ppb
    _max_tvoc = 1187.0  # ppb

    def __init__(
        self,
        name: str,
        bus: int,
        address: int,
        mux: Optional[int] = None,
        channel: Optional[int] = None,
        simulate: bool = False,
        mux_simulator: Optional[MuxSimulator] = None,
    ) -> None:

        # Initialize logger
        self.logger = Logger(name="Driver({})".format(name), dunder_name=__name__)
        self.logger.info("Initializing driver")

        # Check if simulating
        if simulate:
            self.logger.info("Simulating driver")
            Simulator = CCS811Simulator
        else:
            Simulator = None

        # Initialize I2C
        try:
            self.i2c = I2C(
                name=name,
                bus=bus,
                address=address,
                mux=mux,
                channel=channel,
                mux_simulator=mux_simulator,
                PeripheralSimulator=Simulator,
            )
        except I2CError as e:
            message = "Driver unable to initialize"
            raise InitError(message, logger=self.logger) from e

    def setup(self, retry: bool = False):
        """Setups sensor."""
        try:
            self.reset(retry=retry)
            self.check_hardware_id(retry=retry)
            self.start_app(retry=retry)
            # self.check_for_errors(retry=retry)
            self.write_measurement_mode(1, False, False, retry=retry)
            time.sleep(1200)  # Warm up for 20 minutes
        except DriverError as e:
            raise SetupError("Unable to setup", logger=self.logger) from e

    def start_app(self, retry: bool = False):
        """Starts app by writing a byte to the app start register."""
        self.logger.info("Starting app")

        # Write a byte to app start register
        try:
            self.i2c.write(bytes([0xF4]), retry=retry)
        except I2CError as e:
            raise StartAppError("Unable to start app", logger=self.logger) from e

    def read_hardware_id(self, retry: bool = False) -> int:
        """Reads hardware ID from sensor."""
        self.logger.info("Reading hardware ID")

        # Read register
        try:
            return self.i2c.read_register(0x20, retry=retry)
        except I2CError as e:
            message = "Driver unable to read harware id register"
            raise ReadRegisterError(message, logger=self.logger) from e

    def check_hardware_id(self, retry: bool = False) -> None:
        """Checks for valid id in hardware id register."""
        self.logger.info("Checking hardware ID")
        hardware_id = self.read_hardware_id(retry=retry)
        if hardware_id != 0x81:
            raise HardwareIDError("Invalid hardware ID", logger=self.logger)

    def read_status_register(self, retry: bool = False) -> StatusRegister:
        """Reads status of sensor."""
        self.logger.info("Reading status register")

        # Read register
        try:
            byte = self.i2c.read_register(0x00, retry=retry)
        except I2CError as e:
            message = "Driver unable to read status register"
            raise ReadRegisterError(message, logger=self.logger) from e

        # Parse status register byte
        status_register = StatusRegister(
            firmware_mode=bitwise.get_bit_from_byte(7, byte),
            app_valid=bool(bitwise.get_bit_from_byte(4, byte)),
            data_ready=bool(bitwise.get_bit_from_byte(3, byte)),
            error=bool(bitwise.get_bit_from_byte(0, byte)),
        )
        self.logger.debug(status_register)
        return status_register

    def check_for_errors(self, retry: bool = False) -> None:
        """Checks for errors in status register."""
        self.logger.info("Checking for errors")
        status_register = self.read_status_register(retry=retry)
        if status_register.error:
            message = "Error in status register"
            raise StatusError(message, status_register, logger=self.logger)

    def read_error_register(self, retry: bool = False) -> ErrorRegister:
        """Reads error register."""
        self.logger.info("Reading error register")

        # Read register
        try:
            byte = self.i2c.read_register(0x0E, retry=retry)
        except I2CError as e:
            message = "Driver unable to read error register"
            raise ReadRegisterError(message, logger=self.logger) from e

        # Parse error register byte
        return ErrorRegister(
            write_register_invalid=bool(bitwise.get_bit_from_byte(0, byte)),
            read_register_invalid=bool(bitwise.get_bit_from_byte(1, byte)),
            measurement_mode_invalid=bool(bitwise.get_bit_from_byte(2, byte)),
            max_resistance=bool(bitwise.get_bit_from_byte(3, byte)),
            heater_fault=bool(bitwise.get_bit_from_byte(4, byte)),
            heater_supply=bool(bitwise.get_bit_from_byte(5, byte)),
        )

    def write_measurement_mode(
        self,
        drive_mode: int,
        enable_data_ready_interrupt: bool,
        enable_threshold_interrupt: bool,
        retry: bool = False,
    ) -> None:
        """Writes measurement mode to the sensor."""
        self.logger.debug("Writing measurement mode")

        # Initialize bits
        bits = {7: 0, 1: 0, 0: 0}

        # Set drive mode
        if drive_mode == 0:
            bits.update({6: 0, 5: 0, 4: 0})
        elif drive_mode == 1:
            bits.update({6: 0, 5: 0, 4: 1})
        elif drive_mode == 2:
            bits.update({6: 0, 5: 1, 4: 0})
        elif drive_mode == 3:
            bits.update({6: 0, 5: 1, 4: 1})
        elif drive_mode == 4:
            bits.update({6: 1, 5: 0, 4: 0})
        else:
            raise ValueError("Invalid drive mode")

        # Set data ready interrupt
        bits.update({3: int(enable_data_ready_interrupt)})

        # Set threshold interrupt
        bits.update({2: int(enable_data_ready_interrupt)})

        # Convert bits to byte
        sbits = {}
        for key in sorted(bits.keys(), reverse=True):
            sbits[key] = bits[key]
        self.logger.error("bits = {}".format(sbits))  # TODO: remove
        write_byte = bitwise.get_byte_from_bits(bits)
        self.logger.error("write_byte = 0x{:02X}".format(write_byte))  # TODO: remove

        # Write measurement mode to sensor
        try:
            self.i2c.write(bytes([0x01, write_byte]), retry=retry)
        except I2CError as e:
            message = "Unable to write measurement mode"
            raise WriteMeasurementModeError(messsage, logger=self.logger) from e

    def write_environment_data(
        self, temperature=None, humidity=None, retry: bool = False
    ):
        """Writes compensation temperature and / or humidity to sensor."""
        self.logger.debug("Writing environment data")

        # Check valid environment values
        if temperature == None and humidity == None:
            raise ValueError("Temperature and/or humidity value required")

        # Calculate temperature bytes
        if temperature != None:
            temp_msb, temp_lsb = bitwise.convert_base_1_512(temperature + 25)
        else:
            temp_msb = 0x64
            temp_lsb = 0x00

        # Calculate humidity bytes
        if humidity != None:
            hum_msb, hum_lsb = bitwise.convert_base_1_512(humidity)
        else:
            hum_msb = 0x64
            hum_lsb = 0x00

        # Write environment data to sensor
        bytes_ = [0x05, hum_msb, hum_lsb, temp_msb, temp_lsb]
        try:
            self.i2c.write(bytes(bytes_), retry=retry)
        except I2CError as e:
            message = "Unable to write measurement mode"
            raise WriteEnvironmentDataError(messsage, logger=self.logger) from e

    def read_algorithm_data(
        self, retry: bool = False, reread: int = 5
    ) -> Tuple[float, float]:
        """Reads algorighm data from sensor hardware."""
        self.logger.debug("Reading co2/tvoc algorithm data")

        # Read status register
        try:
            status = self.read_status_register()
        except ReadRegisterError as e:
            message = "Unable to read status register"
            raise ReadAlgorithmDataError(message) from e

        # Check if data is ready
        if not status.data_ready:
            if reread:
                self.logger.debug("Data not ready yet, re-reading in 1 second")
                time.sleep(1)
                self.read_algorithm_data(retry=retry, reread=reread - 1)
            else:
                raise ReadAlgorithmDataError("Algorithm data not ready")

        # Get algorithm data
        try:
            self.i2c.write(bytes([0x02]), retry=retry)
            bytes_ = self.i2c.read(4)
        except (WriteError, ReadError):
            raise ReadAlgorithmDataError("Unable to get algorithm data") from e

        # Parse data bytes
        co2 = float(bytes_[0] * 255 + bytes_[1])
        tvoc = float(bytes_[2] * 255 + bytes_[3])

        # Verify co2 value within valid range
        if co2 > self._min_co2 and co2 < self._min_co2:
            raise ReadAlgorithmDataError("CO2 reading outside of valid range")

        # Verify tvos within valid range
        if tvoc > self._min_tvoc and tvoc < self._min_tvoc:
            raise ReadAlgorithmDataError("TVOC reading outside of valid range")

        # Successfully read sensor data!
        self.logger.debug("Carbon Dioxide: {} ppm".format(co2))
        self.logger.debug("Total Volatile Organic Compounds: {} ppb".format(tvoc))
        return co2, tvoc

    def read_raw_data(self) -> None:
        """Reads raw data from sensor."""
        ...

    def read_ntc(self) -> None:
        """ Read value of NTC. Can be used to calculate temperature. """
        ...

    def reset(self, retry: bool = False) -> None:
        """Resets sensor and places into boot mode."""
        self.logger.debug("Resetting sensor")

        # Write reset bytes to sensor
        bytes_ = [0xFF, 0x11, 0xE5, 0x72, 0x8A]
        try:
            self.i2c.write(bytes(bytes_), retry=retry)
        except I2CError as e:
            message = "Unable to reset sensor"
            raise ResetError(messsage, logger=self.logger) from e
