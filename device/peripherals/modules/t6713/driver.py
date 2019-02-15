# Import standard python modules
import time, threading

# Import python types
from typing import NamedTuple, Optional, Tuple

# Import device utilities
from device.utilities import logger, bitwise
from device.utilities.communication.i2c.main import I2C
from device.utilities.communication.i2c.mux_simulator import MuxSimulator
from device.utilities.communication.i2c.exceptions import I2CError

# Import driver elements
from device.peripherals.modules.t6713 import exceptions, simulator


class Status(NamedTuple):
    """Data class for parsed status."""

    error_condition: bool
    flash_error: bool
    calibration_error: bool
    rs232: bool
    rs485: bool
    i2c: bool
    warm_up_mode: bool
    single_point_calibration: bool


class T6713Driver:
    """Driver for t6713 co2 sensor."""

    # Initialize co2 properties
    min_co2 = 10  # ppm
    max_co2 = 5000  # ppm
    warmup_timeout = 120  # seconds

    def __init__(
        self,
        name: str,
        i2c_lock: threading.RLock,
        bus: int,
        address: int,
        mux: Optional[int] = None,
        channel: Optional[int] = None,
        simulate: Optional[bool] = False,
        mux_simulator: Optional[MuxSimulator] = None,
    ) -> None:
        """Initializes t6713 driver."""

        # Initialize parameters
        self.simulate = simulate
        self.i2c_lock = i2c_lock

        # Initialize logger
        logname = "Driver({})".format(name)
        self.logger = logger.Logger(logname, "device")

        # Check if simulating
        if simulate:
            self.logger.info("Simulating driver")
            Simulator = simulator.T6713Simulator
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
        """Sets up sensor."""

        # Set ABC logic state
        try:
            self.enable_abc_logic()
        except exceptions.EnableABCLogicError as e:
            raise exceptions.SetupError(logger=self.logger) from e

        # Wait at least 2 minutes for sensor to stabilize
        start_time = time.time()
        while time.time() - start_time < 120:

            # Keep logs active
            self.logger.info("Warming up, waiting for 2 minutes")

            # Update every few seconds
            time.sleep(3)

            # Break out if simulating
            if self.simulate:
                break

        # Wait for sensor to report exiting warm up mode
        start_time = time.time()
        while True:

            # Keep logs active
            self.logger.info("Warming up, waiting for status")

            # Read status
            try:
                status = self.read_status()
            except exceptions.ReadStatusError as e:
                raise exceptions.SetupError(logger=self.logger) from e

            # Check if sensor completed warm up mode
            if not status.warm_up_mode:
                self.logger.info("Warmup complete")
                break

            # Check if timed out
            if time.time() - start_time > self.warmup_timeout:
                raise exceptions.SetupError(
                    "Warmup period timed out", logger=self.logger
                )

            # Update every 3 seconds
            time.sleep(3)

    def read_co2(self, retry: bool = True) -> Optional[float]:
        """Reads co2 value."""
        self.logger.debug("Reading co2")

        # Read co2 data, requires mux disable to read all x4 bytes
        try:
            with self.i2c_lock:
                self.i2c.write(bytes([0x04, 0x13, 0x8B, 0x00, 0x01]), retry=retry)
                bytes_ = self.i2c.read(4, retry=retry, disable_mux=True)
        except I2CError as e:
            raise exceptions.ReadCo2Error(logger=self.logger) from e

        # Convert co2 data and set significant figures
        _, _, msb, lsb = bytes_
        co2 = float(msb * 256 + lsb)
        co2 = round(co2, 0)

        # Verify co2 value within valid range
        if co2 > self.min_co2 and co2 < self.min_co2:
            self.logger.warning("Co2 outside of valid range")
            return None

        # Successfully read carbon dioxide
        self.logger.debug("Co2: {} ppm".format(co2))
        return co2

    def read_status(self, retry: bool = True) -> Status:
        """Reads status."""
        self.logger.debug("Reading status")

        # Read status data, requires mux diable to read all x4 bytes
        try:
            with self.i2c_lock:
                self.i2c.write(bytes([0x04, 0x13, 0x8A, 0x00, 0x01]), retry=retry)
                bytes_ = self.i2c.read(4, retry=retry, disable_mux=True)
        except I2CError as e:
            raise exceptions.ReadStatusError(logger=self.logger) from e

        # Parse status bytes
        _, _, status_msb, status_lsb = bytes_
        status = Status(
            error_condition=bool(bitwise.get_bit_from_byte(0, status_lsb)),
            flash_error=bool(bitwise.get_bit_from_byte(1, status_lsb)),
            calibration_error=bool(bitwise.get_bit_from_byte(2, status_lsb)),
            rs232=bool(bitwise.get_bit_from_byte(0, status_msb)),
            rs485=bool(bitwise.get_bit_from_byte(1, status_msb)),
            i2c=bool(bitwise.get_bit_from_byte(2, status_msb)),
            warm_up_mode=bool(bitwise.get_bit_from_byte(3, status_msb)),
            single_point_calibration=bool(bitwise.get_bit_from_byte(7, status_msb)),
        )

        # Successfully read status
        self.logger.debug("Status: {}".format(status))
        return status

    def enable_abc_logic(self, retry: bool = True) -> None:
        """Enables ABC logic."""
        self.logger.info("Enabling abc logic")
        try:
            self.i2c.write(bytes([0x05, 0x03, 0xEE, 0xFF, 0x00]), retry=retry)
        except I2CError as e:
            raise exceptions.EnableABCLogicError(logger=self.logger) from e

    def disable_abc_logic(self, retry: bool = True) -> None:
        """Disables ABC logic."""
        self.logger.info("Disabling abc logic")
        try:
            self.i2c.write(bytes([0x05, 0x03, 0xEE, 0x00, 0x00]), retry=retry)
        except I2CError as e:
            raise exceptions.DisableABCLogicError(logger=self.logger) from e

    def reset(self, retry: bool = True) -> None:
        """Initiates soft reset."""
        self.logger.info("Performing soft reset")
        try:
            self.i2c.write(bytes([0x05, 0x03, 0xE8, 0xFF, 0x00]), retry=retry)
        except I2CError as e:
            raise exceptions.ResetError(logger=self.logger) from e
