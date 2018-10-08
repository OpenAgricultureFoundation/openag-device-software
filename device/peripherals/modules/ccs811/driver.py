# Import standard python modules
import time, threading

# Import python variables
from typing import NamedTuple, Optional, Tuple

# Import device utilities
from device.utilities import logger, bitwise
from device.utilities.communication.i2c.main import I2C
from device.utilities.communication.i2c.exceptions import I2CError
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

# Import driver elements
from device.peripherals.modules.ccs811 import simulator, exceptions


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
    """Driver for atlas ccs811 co2 and tvoc."""

    # Initialize variable properties
    min_co2 = 400.0  # ppm
    max_co2 = 8192.0  # ppm
    min_tvoc = 0.0  # ppb
    max_tvoc = 1187.0  # ppb

    def __init__(
        self,
        name: str,
        i2c_lock: threading.RLock,
        bus: int,
        address: int,
        mux: Optional[int] = None,
        channel: Optional[int] = None,
        simulate: bool = False,
        mux_simulator: Optional[MuxSimulator] = None,
    ) -> None:

        # Initialize simulation mode
        self.simulate = simulate

        # Initialize logger
        logname = "Driver({})".format(name)
        self.logger = logger.Logger(logname, "peripherals")
        self.logger.info("Initializing driver")

        # Check if simulating
        if simulate:
            self.logger.info("Simulating driver")
            Simulator = simulator.CCS811Simulator
        else:
            Simulator = None

        # Initialize I2C
        try:
            self.i2c = I2C(
                name=name,
                i2c_lock=i2c_lock,
                bus=bus,
                address=address,
                mux=mux,
                channel=channel,
                mux_simulator=mux_simulator,
                PeripheralSimulator=Simulator,
            )
        except I2CError as e:
            raise exceptions.InitError(logger=self.logger) from e

    def setup(self, retry: bool = True) -> None:
        """Setups sensor."""
        try:
            self.reset(retry=retry)
            self.check_hardware_id(retry=retry)
            self.start_app(retry=retry)
            # self.check_for_errors(retry=retry)
            self.write_measurement_mode(1, False, False, retry=retry)

            # Wait 20 minutes for sensor to stabilize
            start_time = time.time()
            while time.time() - start_time < 1200:

                # Keep logs active
                self.logger.info("Warming up, waiting for 20 minutes")

                # Update every 30 seconds
                time.sleep(30)

                # Break out if simulating
                if self.simulate:
                    break

        except exceptions.DriverError as e:
            raise exceptions.SetupError(logger=self.logger) from e

    def start_app(self, retry: bool = True) -> None:
        """Starts app by writing a byte to the app start register."""
        self.logger.info("Starting app")
        try:
            self.i2c.write(bytes([0xF4]), retry=retry)
        except I2CError as e:
            raise exceptions.StartAppError(logger=self.logger) from e

    def read_hardware_id(self, retry: bool = True) -> int:
        """Reads hardware ID from sensor."""
        self.logger.info("Reading hardware ID")
        try:
            return int(self.i2c.read_register(0x20, retry=retry))
        except I2CError as e:
            raise exceptions.ReadRegisterError(
                message="hw id reg", logger=self.logger
            ) from e

    def check_hardware_id(self, retry: bool = True) -> None:
        """Checks for valid id in hardware id register."""
        self.logger.info("Checking hardware ID")
        hardware_id = self.read_hardware_id(retry=retry)
        if hardware_id != 0x81:
            raise exceptions.HardwareIDError(logger=self.logger)

    def read_status_register(self, retry: bool = True) -> StatusRegister:
        """Reads status of sensor."""
        self.logger.info("Reading status register")
        try:
            byte = self.i2c.read_register(0x00, retry=retry)
        except I2CError as e:
            raise exceptions.ReadRegisterError(
                message="status reg", logger=self.logger
            ) from e

        # Parse status register byte
        status_register = StatusRegister(
            firmware_mode=bitwise.get_bit_from_byte(7, byte),
            app_valid=bool(bitwise.get_bit_from_byte(4, byte)),
            data_ready=bool(bitwise.get_bit_from_byte(3, byte)),
            error=bool(bitwise.get_bit_from_byte(0, byte)),
        )
        self.logger.debug(str(status_register))
        return status_register

    def check_for_errors(self, retry: bool = True) -> None:
        """Checks for errors in status register."""
        self.logger.info("Checking for errors")
        status_register = self.read_status_register(retry=retry)
        if status_register.error:
            raise exceptions.StatusError(message=status_register, logger=self.logger)

    def read_error_register(self, retry: bool = True) -> ErrorRegister:
        """Reads error register."""
        self.logger.info("Reading error register")
        try:
            byte = self.i2c.read_register(0x0E, retry=retry)
        except I2CError as e:
            raise exceptions.ReadRegisterError(
                message="error reg", logger=self.logger
            ) from e

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
        retry: bool = True,
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
            raise exceptions.WriteMeasurementModeError(logger=self.logger) from e

    def write_environment_data(
        self,
        temperature: Optional[float] = None,
        humidity: Optional[float] = None,
        retry: bool = True,
    ) -> None:
        """Writes compensation temperature and / or humidity to sensor."""
        self.logger.debug("Writing environment data")

        # Check valid environment values
        if temperature == None and humidity == None:
            raise ValueError("Temperature and/or humidity value required")

        # Calculate temperature bytes
        if temperature != None:
            t = temperature
            temp_msb, temp_lsb = bitwise.convert_base_1_512(t + 25)  # type: ignore
        else:
            temp_msb = 0x64
            temp_lsb = 0x00

        # Calculate humidity bytes
        if humidity != None:
            hum_msb, hum_lsb = bitwise.convert_base_1_512(humidity)  # type: ignore
        else:
            hum_msb = 0x64
            hum_lsb = 0x00

        # Write environment data to sensor
        bytes_ = [0x05, hum_msb, hum_lsb, temp_msb, temp_lsb]
        try:
            self.i2c.write(bytes(bytes_), retry=retry)
        except I2CError as e:
            raise exceptions.WriteEnvironmentDataError(logger=self.logger) from e

    def read_algorithm_data(
        self, retry: bool = True, reread: int = 5
    ) -> Tuple[float, float]:
        """Reads algorighm data from sensor hardware."""
        self.logger.debug("Reading co2/tvoc algorithm data")

        # Read status register
        try:
            status = self.read_status_register()
        except exceptions.ReadRegisterError as e:
            raise exceptions.ReadAlgorithmDataError(logger=self.logger) from e

        # Check if data is ready
        if not status.data_ready:
            if reread:
                self.logger.debug("Data not ready yet, re-reading in 1 second")
                time.sleep(1)
                self.read_algorithm_data(retry=retry, reread=reread - 1)
            else:
                message = "data not ready"
                raise exceptions.ReadAlgorithmDataError(
                    message=message, logger=self.logger
                )

        # Get algorithm data
        try:
            self.i2c.write(bytes([0x02]), retry=retry)
            bytes_ = self.i2c.read(4)
        except I2CError:
            raise exceptions.ReadAlgorithmDataError(logger=self.logger) from e

        # Parse data bytes
        co2 = float(bytes_[0] * 255 + bytes_[1])
        tvoc = float(bytes_[2] * 255 + bytes_[3])

        # Verify co2 value within valid range
        if co2 > self.min_co2 and co2 < self.min_co2:
            message = "CO2 reading outside of valid range"
            raise exceptions.ReadAlgorithmDataError(message=message, logger=self.logger)

        # Verify tvos within valid range
        if tvoc > self.min_tvoc and tvoc < self.min_tvoc:
            message = "TVOC reading outside of valid range"
            raise exceptions.ReadAlgorithmDataError(message=message, logger=self.logger)

        # Successfully read sensor data!
        self.logger.debug("CO2: {} ppm".format(co2))
        self.logger.debug("TVOC: {} ppb".format(tvoc))
        return co2, tvoc

    def read_raw_data(self) -> None:
        """Reads raw data from sensor."""
        ...

    def read_ntc(self) -> None:
        """ Read value of NTC. Can be used to calculate temperature. """
        ...

    def reset(self, retry: bool = True) -> None:
        """Resets sensor and places into boot mode."""
        self.logger.debug("Resetting sensor")

        # Write reset bytes to sensor
        bytes_ = [0xFF, 0x11, 0xE5, 0x72, 0x8A]
        try:
            self.i2c.write(bytes(bytes_), retry=retry)
        except I2CError as e:
            raise exceptions.ResetError(logger=self.logger) from e
