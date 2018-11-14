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
from device.peripherals.modules.atlas_co2 import simulator, exceptions

ATLAS_CO2_DEVICE_TYPE = "co2"


class AtlasCo2Driver(driver.AtlasDriver):
    """Driver for atlas co2 sensor."""

    # Initialize sensor properties
    co2_accuracy = 30  # ppm
    min_co2 = 0  # ppm
    max_co2 = 10000  # ppm
    warmup_timeout = 300  # seconds -> 5 minutes

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
        """Initializes driver."""

        # Check if simulating
        if simulate:
            Simulator = simulator.AtlasCo2Simulator
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
            self.enable_protocol_lock(retry=retry)
            self.enable_led(retry=retry)
            self.disable_alarm(retry=retry)

            # Verify sensor is a co2 sensor
            info = self.read_info(retry=retry)
            if info.sensor_type != "co2":
                message = "Not an Atlas CO2 sensor"
                raise exceptions.SetupError(message=message, logger=self.logger)

            # Enable internal temperature reporting
            self.enable_internal_temperature()

            # Wait for at least 10 minutes for sensor to warm up
            start_time = time.time()
            while time.time() - start_time < 600:

                # Keep logs active
                self.logger.debug("Warming up, waiting 10 minutes")

                # Check if simulating
                if self.simulate:
                    self.logger.debug("Simulated 10 minute wait")
                    break

                # Update every minute
                time.sleep(60)

            # Get initial internal temperature measurement
            self.logger.debug("Taking initial internal temperature reading")
            prev_internal_temperature = self.read_internal_temperature()

            # Wait for a minute if not simulating
            if not self.simulate:
                time.sleep(60)

            # Wait for sensor to report stable internal temperature
            start_time = time.time()
            while True:

                # Keep logs active
                self.logger.debug("Warming up, waiting for stable internal temperature")

                # Check if prev internal temperature within half a degree of current
                internal_temperature = self.read_internal_temperature()
                temp_delta = abs(internal_temperature - prev_internal_temperature)
                self.logger.debug("temp delta = {}".format(temp_delta))
                if temp_delta < 0.5:
                    self.logger.debug("Internal temperature stabilized")
                    self.disable_internal_temperature()
                    return

                # Check for timeout
                if time.time() - start_time > self.warmup_timeout:
                    self.disable_internal_temperature()
                    message = "Internal temperature did not stabilize, timed out"
                    raise exceptions.SetupError(message=message, logger=self.logger)

                # Update every minute
                time.sleep(60)

        except Exception as e:
            raise exceptions.SetupError(logger=self.logger) from e

    def read_co2(self, retry: bool = True) -> Optional[float]:
        """Reads co2 value."""
        self.logger.debug("Reading Co2")

        # Get co2 reading from hardware
        try:
            response = self.process_command("R", process_seconds=0.6, retry=retry)
        except Exception as e:
            raise exceptions.ReadCo2Error(logger=self.logger) from e

        # Check internal temp not reported
        if "," in response:
            self.logger.warning("Internal temperature reporting not disabled")
            response = response.split(",")[0]

        # Parse response
        co2_raw = float(response)  # type: ignore

        # Round to 0 decimal places
        co2 = round(co2_raw, 0)

        # Verify tempreature value within valid range
        if co2 > self.min_co2 and co2 < self.min_co2:
            self.logger.warning("Temperature outside of valid range")
            return None

        # Successfully read co2
        self.logger.debug("CO2: {} ppm".format(co2))
        return co2

    def read_internal_temperature(self, retry: bool = True) -> Optional[float]:
        """Reads internal temperature value."""
        self.logger.debug("Reading internal temperature")

        # Get internal temperature reading from hardware
        try:
            response = self.process_command("R", process_seconds=0.6, retry=retry)
        except Exception as e:
            raise exceptions.ReadInternalTemperatureError(logger=self.logger) from e

        # Verify internal temp is reported
        if "," not in response:
            message = "internal temperature not enabled"
            raise exceptions.ReadInternalTemperatureError(
                message=message, logger=logger
            )

        # Parse response
        internal_temperature_raw = float(response.split(",")[1])  # type: ignore

        # Round to 2 decimal places
        internal_temperature = round(internal_temperature_raw, 2)

        # Successfully read internal temperature
        self.logger.debug("Internal Temp: {} C".format(internal_temperature))
        return internal_temperature

    def enable_internal_temperature(self, retry: bool = True) -> None:
        """Enables internal temperature."""
        self.logger.info("Enabling internal temperature")
        try:
            self.process_command("O,t,1", process_seconds=0.6, retry=retry)
        except Exception as e:
            raise exceptions.EnableInternalTemperatureError(logger=self.logger) from e

    def disable_internal_temperature(self, retry: bool = True) -> None:
        """Disables internal temperature."""
        self.logger.info("Disabling internal temperature")
        try:
            self.process_command("O,t,0", process_seconds=0.6, retry=retry)
        except Exception as e:
            raise exceptions.DisableInternalTemperatureError(logger=self.logger) from e

    def enable_alarm(self, retry: bool = True) -> None:
        """Enables alarm."""
        self.logger.info("Enabling alarm")
        try:
            self.process_command("Alarm,en,1", process_seconds=0.6, retry=retry)
        except Exception as e:
            raise exceptions.EnableAlarmError(logger=self.logger) from e

    def disable_alarm(self, retry: bool = True) -> None:
        """Disables alarm."""
        self.logger.info("Disabling alarm")
        try:
            self.process_command("Alarm,en,0", process_seconds=0.6, retry=retry)
        except Exception as e:
            raise exceptions.DisableAlarmError(logger=self.logger) from e
