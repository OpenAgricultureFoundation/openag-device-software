# Import standard python modules
import time, threading

# Import python types
from typing import Optional, Tuple, Dict, NamedTuple

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.communication.i2c.main import I2C
from device.utilities.communication.i2c.exceptions import I2CError
from device.utilities.communication.i2c.mux_simulator import MuxSimulator
from device.utilities.communication.i2c.peripheral_simulator import PeripheralSimulator

# Import manager elements
from device.peripherals.classes.atlas import exceptions


class Info(NamedTuple):
    """Data class for parsed info register."""

    sensor_type: str
    firmware_version: float


class Status(NamedTuple):
    """Data class for parsed status register."""

    prev_restart_reason: str
    voltage: float


class AtlasDriver:
    """Parent class for atlas drivers."""

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
        Simulator: Optional[PeripheralSimulator] = None,
    ) -> None:
        """ Initializes atlas driver. """

        # Initialize parameters
        self.simulate = simulate

        # Initialize logger
        logname = "Driver({})".format(name)
        self.logger = Logger(logname, "peripherals")

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
            raise exceptions.InitError(logger=self.logger)

    def setup(self, retry: bool = True) -> None:
        """Setsup sensor."""
        self.logger.debug("Setting up sensor")
        try:
            self.enable_led()
            info = self.read_info()
            if info.firmware_version > 1.94:
                self.enable_protocol_lock()
        except Exception as e:
            raise exceptions.SetupError(logger=self.logger) from e

    def process_command(
        self,
        command_string: str,
        process_seconds: float,
        num_bytes: int = 31,
        retry: bool = True,
        read_response: bool = True,
    ) -> Optional[str]:
        """Sends command string to device, waits for processing seconds, then
        tries to read num response bytes with optional retry if device
        returns a `still processing` response code. Read retry is enabled 
        by default. Returns response string on success or raises exception 
        on error."""
        self.logger.debug("Processing command: {}".format(command_string))

        try:
            # Send command to device
            byte_array = bytearray(command_string + "\00", "utf8")
            self.i2c.write(bytes(byte_array), retry=retry)

            # Check if reading response
            if read_response:
                return self.read_response(process_seconds, num_bytes, retry=retry)

            # Otherwise return none
            return None

        except Exception as e:
            raise exceptions.ProcessCommandError(logger=self.logger) from e

    def read_response(
        self, process_seconds: float, num_bytes: int, retry: bool = True
    ) -> str:
        """Reads response from from device. Waits processing seconds then 
        tries to read num response bytes with optional retry. Returns 
        response string on success or raises exception on error."""

        # Give device time to process
        self.logger.debug("Waiting for {} seconds".format(process_seconds))
        time.sleep(process_seconds)

        # Read device dataSet
        try:
            self.logger.debug("Reading response")
            data = self.i2c.read(num_bytes)
        except Exception as e:
            raise exceptions.ReadResponseError(logger=self.logger) from e

        # Format response code
        response_code = int(data[0])

        # Check for invalid syntax
        if response_code == 2:
            message = "invalid command string syntax"
            raise exceptions.ReadResponseError(message=message, logger=self.logger)

        # Check if still processing
        elif response_code == 254:

            # Try to read one more time if retry enabled
            if retry == True:
                self.logger.debug("Sensor still processing, retrying read")
                return self.read_response(process_seconds, num_bytes, retry=False)
            else:
                message = "insufficient processing time"
                raise exceptions.ReadResponseError(message, logger=self.logger)

        # Check if device has no data to send
        elif response_code == 255:

            # Try to read one more time if retry enabled
            if retry == True:
                self.logger.warning("Sensor reported no data to read, retrying read")
                return self.read_response(process_seconds, num_bytes, retry=False)
            else:
                message = "insufficient processing time"
                raise exceptions.ReadResponseError(message=message, logger=self.logger)

        # Invalid response code
        elif response_code != 1:
            message = "invalid response code"
            raise exceptions.ReadResponseError(message=message, logger=self.logger)

        # Successfully read response
        response_message = str(data[1:].decode("utf-8").strip("\x00"))
        self.logger.debug("Response:`{}`".format(response_message))
        return response_message

    def read_info(self, retry: bool = True) -> Info:
        """Read sensor info register containing sensor type and firmware version. e.g. EC, 2.0."""
        self.logger.debug("Reading info register")

        # Send command
        try:
            response = self.process_command("i", process_seconds=0.3, retry=retry)
        except Exception as e:
            raise exceptions.ReadInfoError(logger=self.logger) from e

        # Parse response
        _, sensor_type, firmware_version = response.split(",")  # type: ignore
        firmware_version = float(firmware_version)

        # Store firmware version
        self.firmware_version = firmware_version

        # Create info dataclass
        info = Info(sensor_type=sensor_type.lower(), firmware_version=firmware_version)

        # Successfully read info
        self.logger.debug(str(info))
        return info

    def read_status(self, retry: bool = True) -> Status:
        """Reads status from device."""
        self.logger.debug("Reading status register")
        try:
            response = self.process_command("Status", process_seconds=0.3, retry=retry)
        except Exception as e:
            raise exceptions.ReadStatusError(logger=self.logger) from e

        # Parse response message
        command, code, voltage = response.split(",")  # type: ignore

        # Break out restart code
        if code == "P":
            prev_restart_reason = "Powered off"
            self.logger.debug("Device previous restart due to powered off")
        elif code == "S":
            prev_restart_reason = "Software reset"
            self.logger.debug("Device previous restart due to software reset")
        elif code == "B":
            prev_restart_reason = "Browned out"
            self.logger.critical("Device browned out on previous restart")
        elif code == "W":
            prev_restart_reason = "Watchdog"
            self.logger.debug("Device previous restart due to watchdog")
        elif code == "U":
            self.prev_restart_reason = "Unknown"
            self.logger.warning("Device previous restart due to unknown")

        # Build status data class
        status = Status(prev_restart_reason=prev_restart_reason, voltage=float(voltage))

        # Successfully read status
        self.logger.debug(str(status))
        return status

    def enable_protocol_lock(self, retry: bool = True) -> None:
        """Enables protocol lock."""
        self.logger.debug("Enabling protocol lock")
        try:
            self.process_command("Plock,1", process_seconds=0.9, retry=retry)
        except Exception as e:
            raise exceptions.EnableProtocolLockError(logger=self.logger) from e

    def disable_protocol_lock(self, retry: bool = True) -> None:
        """Disables protocol lock."""
        self.logger.debug("Disabling protocol lock")
        try:
            self.process_command("Plock,0", process_seconds=0.9, retry=retry)
        except Exception as e:
            raise exceptions.DisableProtocolLockError(logger=self.logger) from e

    def enable_led(self, retry: bool = True) -> None:
        """Enables led."""
        self.logger.debug("Enabling led")
        try:
            self.process_command("L,1", process_seconds=1.8, retry=retry)
        except Exception as e:
            raise exceptions.EnableLEDError(logger=self.logger) from e

    def disable_led(self, retry: bool = True) -> None:
        """Disables led."""
        self.logger.debug("Disabling led")
        try:
            self.process_command("L,0", process_seconds=1.8, retry=retry)
        except Exception as e:
            raise exceptions.DisableLEDError(logger=self.logger) from e

    def enable_sleep_mode(self, retry: bool = True) -> None:
        """Enables sleep mode, sensor will wake up by sending any command to it."""
        self.logger.debug("Enabling sleep mode")

        # Send command
        try:
            self.process_command(
                "Sleep", process_seconds=0.3, read_response=False, retry=retry
            )
        except Exception as e:
            raise exceptions.EnableSleepModeError(logger=self.logger) from e

    def set_compensation_temperature(
        self, temperature: float, retry: bool = True
    ) -> None:
        """Sets compensation temperature."""
        self.logger.debug("Setting compensation temperature")
        try:
            command = "T,{}".format(temperature)
            self.process_command(command, process_seconds=0.3, retry=retry)
        except Exception as e:
            raise exceptions.SetCompensationTemperatureError(logger=self.logger) from e

    def calibrate_low(self, value: float, retry: bool = True) -> None:
        """Takes a low point calibration reading."""
        self.logger.debug("Taking low point calibration reading")
        try:
            command = "Cal,low,{}".format(value)
            self.process_command(command, process_seconds=0.9, retry=retry)
        except Exception as e:
            raise exceptions.TakeLowPointCalibrationError(logger=self.logger) from e

    def calibrate_mid(self, value: float, retry: bool = True) -> None:
        """Takes a mid point calibration reading."""
        self.logger.debug("Taking mid point calibration reading")
        try:
            command = "Cal,mid,{}".format(value)
            self.process_command(command, process_seconds=0.9, retry=retry)
        except Exception as e:
            raise exceptions.TakeMidPointCalibrationError(logger=self.logger) from e

    def calibrate_high(self, value: float, retry: bool = True) -> None:
        """Takes a high point calibration reading."""
        self.logger.debug("Taking high point calibration reading")
        try:
            command = "Cal,high,{}".format(value)
            self.process_command(command, process_seconds=0.9, retry=retry)
        except Exception as e:
            raise exceptions.TakeHighPointCalibrationError(logger=self.logger) from e

    def clear_calibrations(self, retry: bool = True) -> None:
        """Clears calibration readings."""
        self.logger.debug("Clearing calibration readings")
        try:
            self.process_command("Cal,clear", process_seconds=0.9, retry=retry)
        except Exception as e:
            raise exceptions.ClearCalibrationError(logger=self.logger) from e

    def factory_reset(self, retry: bool = True) -> None:
        """Resets sensor to factory config."""
        self.logger.debug("Performing factory reset")
        try:
            self.process_command(
                "Factory", process_seconds=0.3, read_response=False, retry=retry
            )
        except Exception as e:
            raise exceptions.FactoryResetError(logger=self.logger) from e
