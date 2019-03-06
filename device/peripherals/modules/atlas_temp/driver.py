# Import standard python modules
import time, threading

# Import python types
from typing import Optional, Tuple, NamedTuple

# Import device utilities
from device.utilities import maths
from device.utilities.communication.i2c.main import I2C
from device.utilities.communication.i2c.exceptions import I2CError
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

# Import module elements
from device.peripherals.classes.atlas import driver
from device.peripherals.modules.atlas_temp import simulator, exceptions


class AtlasTempDriver(driver.AtlasDriver):
    """Driver for atlas temperature sensor."""

    # Initialize sensor properties
    temperature_accuracy = 0.1  # deg C
    min_temperature = -126.0
    max_temperature = 1254.0

    def __init__(
        self,
        name: str,
        i2c_lock: threading.RLock,
        address: int,
        bus: Optional[int] = None,
        mux: Optional[int] = None,
        channel: Optional[int] = None,
        simulate: bool = False,
        mux_simulator: Optional[MuxSimulator] = None,
    ) -> None:
        """ Initializes driver. """

        # Check if simulating
        if simulate:
            Simulator = simulator.AtlasTempSimulator
        else:
            Simulator = None

        # Initialize parent class
        super().__init__(
            name=name,
            i2c_lock=i2c_lock,
            bus=bus,
            address=address,
            mux=mux,
            channel=channel,
            simulate=simulate,
            mux_simulator=mux_simulator,
            Simulator=Simulator,
        )

    def setup(self, retry: bool = True) -> None:
        """Sets up sensor."""
        self.logger.info("Setting up sensor")
        try:
            self.enable_led(retry=retry)
            info = self.read_info(retry=retry)
            if info.firmware_version > 1.94:
                self.enable_protocol_lock(retry=retry)
            self.set_temperature_scale_celsius(retry=retry)
            self.disable_data_logger(retry=retry)
        except Exception as e:
            raise exceptions.SetupError(logger=self.logger) from e

    def read_temperature(self, retry: bool = True) -> Optional[float]:
        """Reads temperature value."""
        self.logger.debug("Reading Temperature")

        # Get temperature reading from hardware
        # Assumes temperature output is in celsius
        try:
            response = self.process_command("R", process_seconds=0.6, retry=retry)
        except Exception as e:
            raise exceptions.ReadTemperatureError(logger=self.logger) from e

        # Parse response
        temperature_raw = float(response)  # type: ignore

        # Round to 2 decimal places
        temperature = round(temperature_raw, 2)

        # Verify tempreature value within valid range
        if temperature > self.min_temperature and temperature < self.min_temperature:
            self.logger.warning("Temperature outside of valid range")
            return None

        # Successfully read temperature
        self.logger.debug("Temp: {} C".format(temperature))
        return temperature

    def enable_data_logger(self, retry: bool = True) -> None:
        """Enables data logger."""
        self.logger.info("Disabling data logger")
        try:
            self.process_command("D,1", process_seconds=0.6, retry=retry)
        except Exception as e:
            raise exceptions.EnableDataLoggerError(logger=self.logger) from e

    def disable_data_logger(self, retry: bool = True) -> None:
        """Disables data logger."""
        self.logger.info("Disabling data logger")
        try:
            self.process_command("D,0", process_seconds=0.6, retry=retry)
        except Exception as e:
            raise exceptions.DisableDataLoggerError(logger=self.logger) from e

    def set_temperature_scale_celsius(self, retry: bool = True) -> None:
        """Sets temperature scale to celsius."""
        self.logger.info("Setting temperature scale to celsius")
        try:
            self.process_command("S,c", process_seconds=0.3, retry=retry)
        except Exception as e:
            raise exceptions.SetTemperatureScaleCelsiusError(logger=self.logger) from e

    def set_temperature_scale_farenheit(self, retry: bool = True) -> None:
        """Sets temperature scale to celsius."""
        self.logger.info("Setting temperature scale to farenheit")
        try:
            self.process_command("S,f", process_seconds=0.3, retry=retry)
        except Exception as e:
            raise exceptions.SetTemperatureScaleFarenheitError(
                logger=self.logger
            ) from e

    def set_temperature_scale_kelvin(self, retry: bool = True) -> None:
        """Sets temperature scale to kelvin."""
        self.logger.info("Setting temperature scale to kelvin")
        try:
            self.process_command("S,k", process_seconds=0.3, retry=retry)
        except Exception as e:
            raise exceptions.SetTemperatureScaleKelvinError(logger=self.logger) from e

    def calibrate(self, value: float, retry: bool = True) -> None:
        """Take a calibration reading."""
        self.logger.info("Calibrating")
        try:
            command = "Cal,{}".format(value)
            self.process_command(command, process_seconds=2.0, retry=retry)
        except Exception as e:
            raise exceptions.CalibrationError(logger=self.logger) from e
