# Import standard python modules
import time, threading

# Import python types
from typing import NamedTuple, Optional, Tuple

# Import device utilities
from device.utilities import logger, bitwise
from device.utilities.communication.i2c.main import I2C
from device.utilities.communication.i2c.exceptions import I2CError
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

# Import driver elements
from device.peripherals.modules.adafruit_soil import simulator, exceptions


class AdafruitSoilDriver:
    """Driver for Adafruit Capacitive STEMMA Soil Sensor"""

    # Initialize variable properties
    min_moisture = 0
    max_moisture = 4095

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
        """Initializes driver."""

        # Initialize logger
        logname = "Driver({})".format(name)
        self.logger = logger.Logger(logname, "peripherals")

        # Check if simulating
        if simulate:
            self.logger.info("Simulating driver")
            Simulator = simulator.AdafruitSoilSimulator
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
                verify_device=False,  # need to write before device responds to read
            )
            # self.read_user_register(retry=True) is found in sht25 driver
        except I2CError as e:
            raise exceptions.InitError(logger=self.logger) from e

    def read_hardware_id(self, retry: bool = True) -> Optional[int]:
        """read the hardware id"""
        self.logger.debug("Reading hardware id")

        try:
            self.i2c.write(bytes([0x00, 0x01]), retry=retry)
        except I2CError as e:
            raise exceptions.ReadHwIdError(logger=self.logger) from e

        # Wait for sensor to process, from Adafruit arduino lib for seesaw
        time.sleep(0.001)

        try:
            bytes_ = self.i2c.read(2, retry=retry)
        except I2CError as e:
            raise exceptions.ReadHwIdError(logger=self.logger) from e

        hwid = int.from_bytes(bytes_, byteorder="big", signed=False)

        return hwid

    def read_moisture(
        self, retry: bool = True, total_sample_attempts: int = 3
    ) -> Optional[int]:
        """read the moisture capacitive value"""

        try:
            self.i2c.write(bytes([0x0F, 0x10]), retry=retry)
        except I2CError as e:
            raise exceptions.ReadMoistureError(logger=self.logger) from e

        time.sleep(0.005)

        try:
            bytes_ = self.i2c.read(2, retry=retry)
        except I2CError as e:
            raise exceptions.ReadMoistureError(logger=self.logger) from e

        raw = int.from_bytes(bytes_, byteorder="big", signed=False)

        #  if raw is out of bounds, try again or throw an exception
        if raw > self.max_moisture:
            if total_sample_attempts > 0:
                time.sleep(0.001)
                return self.read_moisture(
                    retry=retry, total_sample_attempts=total_sample_attempts - 1
                )
            else:
                raise exceptions.BadMoistureReading(logger=self.logger)

        return raw

    def read_temperature(self, retry: bool = True) -> Optional[float]:
        """read temperature value"""

        try:
            self.i2c.write(bytes([0x00, 0x04]), retry=retry)
        except I2CError as e:
            raise exceptions.ReadTemperatureError(logger=self.logger) from e

        # Wait for sensor to process, from Adafruit arduino lib for seesaw
        time.sleep(0.001)

        try:
            bytes_ = self.i2c.read(4, retry=retry)
        except I2CError as e:
            raise exceptions.ReadTemperatureError(logger=self.logger) from e

        raw = int.from_bytes(bytes_, byteorder="big", signed=False)
        # convert to float (bottom 16bits is decimal)
        return (1.0 / (1 << 16)) * raw

    def reset(self, retry: bool = True) -> None:
        """Initiates soft reset."""
        self.logger.info("Initiating soft reset")

        # Send reset command
        try:
            self.i2c.write(bytes([0x00, 0x7F]), retry=retry)
        except I2CError as e:
            raise exceptions.ResetError(logger=self.logger) from e
