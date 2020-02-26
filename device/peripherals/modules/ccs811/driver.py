# Import standard python modules
import struct
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
    min_co2 = 380.0  # ppm
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

        # Initialize i2c lock
        self.i2c_lock = i2c_lock

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
        write_byte = bitwise.get_byte_from_bits(bits)

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
        self.logger.debug("Writing environment data temp: {} humidity: {}".format(temperature, humidity))

        # Check valid environment values
        if temperature is None or humidity is None:
            raise ValueError("Temperature and humidity value required")

        # SRM trying code from Adafruit driver as a test
        # Humidity is stored as an unsigned 16 bits in 1/512%RH. The default
        # value is 50% = 0x64, 0x00. As an example 48.5% humidity would be 0x61,
        # 0x00.
        humidity = int(humidity * 512)

        # Temperature is stored as an unsigned 16 bits integer in 1/512 degrees
        # there is an offset: 0 maps to -25C. The default value is 25C = 0x64,
        # 0x00. As an example 23.5% temperature would be 0x61, 0x00.
        temperature = int((temperature + 25) * 512)

        buf = bytearray(5)
        buf[0] = 0x05
        struct.pack_into(">HH", buf, 1, humidity, temperature)

        # Calculate temperature bytes
        # SRM: This is the wrong approach. We shouldn't be defaulting here, we should use what ever the
        #       previous value was, so we'll require both to be set and let the manager set the value to current
        #       or previous. Otherwise we could just be undoing stuff.
        #if temperature != None:
        #    t = temperature
        #    temp_msb, temp_lsb = bitwise.convert_base_1_512(t + 25)  # type: ignore
        #else:
        #    temp_msb = 0x64
        #    temp_lsb = 0x00

        # Calculate humidity bytes
        #if humidity != None:
        #    hum_msb, hum_lsb = bitwise.convert_base_1_512(humidity)  # type: ignore
        #else:
        #    hum_msb = 0x64
        #    hum_lsb = 0x00

        # Write environment data to sensor
        #bytes_ = [0x05, hum_msb, hum_lsb, temp_msb, temp_lsb]
        try:
            #self.i2c.write(bytes(bytes_), retry=retry)
            self.i2c.write(buf, retry=retry)
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

        # TODO: This shouldn't be recursive, otherwise we'll end up reading multiple times after the fact
        # Check if data is ready
        if not status.data_ready:
            if reread:
                self.logger.debug("Data not ready yet, re-reading in 1 second")
                time.sleep(1)
                self.read_algorithm_data(retry=retry, reread=reread - 1)
            else:
                self.logger.debug("Data not ready yet, skipping reading")
                return None, None

        # Get algorithm data
        try:
            with self.i2c_lock:
                self.i2c.write(bytes([0x02]), retry=retry)
                bytes_ = self.i2c.read(4)
            self.logger.debug("CO2 MSB: 0x{:02X}".format(bytes_[0]))
            self.logger.debug("CO2 LSB: 0x{:02X}".format(bytes_[1]))
            self.logger.debug("TVOC MSB: 0x{:02X}".format(bytes_[2]))
            self.logger.debug("TVOC LSB: 0x{:02X}".format(bytes_[3]))
        except I2CError:
            raise exceptions.ReadAlgorithmDataError(logger=self.logger) from e

        # Check if the i2c data lines aren't getting pulled low fast enough
        # TODO: Investigate this from the hardware lens
        # HACK: Always set the first co2 bit of the first byte to low
        if bytes_[0] > 0x80:
            self.logger.warning('Detected i2c data line fault, masking first co2 bit')
            co2 = float((bytes_[0] - 0x80)* 256 + bytes_[1])
        else:
            co2 = float(bytes_[0] * 256 + bytes_[1])

        # HACK: Always set the first tvoc bit of the first byte to low
        if bytes_[2] > 0x80:
            self.logger.warning('Detected i2c data line fault, masking first tvoc bit')
            tvoc = float((bytes_[2] - 0x80)* 256 + bytes_[3])
        else:
            tvoc = float(bytes_[2] * 256 + bytes_[3])

        # Verify co2 value within valid range
        if co2 < self.min_co2 or co2 > self.max_co2:
            self.logger.warning(f"CO2: Outside of valid range: {co2}")
            co2 = None
        else:
            self.logger.debug("CO2: {} ppm".format(co2))

        # Verify tvoc within valid range
        if tvoc < self.min_tvoc or tvoc > self.max_tvoc:
            self.logger.warning(f"TVOC: Outside of valid range: {tvoc}")
            tvoc = None
        else:
            self.logger.debug("TVOC: {} ppb".format(tvoc))

        # Successfully read sensor data
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
