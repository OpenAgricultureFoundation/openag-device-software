# Import standard python modules
import time
from typing import Optional, Tuple, NamedTuple

# Import device comms
from device.comms.i2c2.main import I2C
from device.comms.i2c2.exceptions import I2CError
from device.comms.i2c2.mux_simulator import MuxSimulator

# Import device utilities
from device.utilities.logger import Logger
from device.utilities import maths

# Import module elements
from device.peripherals.classes.atlas.driver import AtlasDriver
from device.peripherals.modules.atlas_ec.simulator import AtlasECSimulator
from device.peripherals.classes.atlas.exceptions import SetupError
from device.peripherals.modules.atlas_ec.exceptions import (
    ReadECError,
    EnableECOutputError,
    DisableECOutputError,
    EnableTDSOutputError,
    DisableTDSOutputError,
    EnableSalinityOutputError,
    DisableSalinityOutputError,
    EnableSpecificGravityOutputError,
    DisableSpecificGravityOutputError,
    TakeDryCalibrationError,
    TakeSinglePointCalibrationError,
)


class AtlasECDriver(AtlasDriver):
    """ Driver for atlas ec sensor. """

    # Initialize sensor properties
    ec_accuracy_percent = 2
    min_ec = 0.005
    max_ec = 200

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
        """ Initializes driver. """

        # Check if simulating
        if simulate:
            Simulator = AtlasECSimulator
        else:
            Simulator = None

        # Initialize parent class
        super().__init__(
            name=name,
            bus=bus,
            address=address,
            mux=mux,
            channel=channel,
            simulate=simulate,
            mux_simulator=mux_simulator,
            Simulator=Simulator,
        )

    def setup(self) -> None:
        """Sets up sensor."""
        self.logger.info("Setting up sensor")
        try:
            self.enable_led()
            info = self.read_info()
            if info.firmware_version > 1.94:
                self.enable_protocol_lock()
            self.enable_ec_output()
            self.disable_tds_output()
            self.disable_salinity_output()
            self.disable_specific_gravity_output()
        except Exception as e:
            raise SetupError(logger=self.logger) from e

    def read_ec(self, retry: bool = True) -> Optional[float]:
        """ Reads ec from sensor, sets significant 
            figures based off error magnitude, returns value in mS/cm. """
        self.logger.info("Reading EC")

        # Get ec reading from hardware
        # Assumes ec is only enabled output
        try:
            ec_raw = self.process_command("R", process_seconds=0.6, retry=retry)
        except Exception as e:
            message = "Driver unable to read ec"
            raise ReadECError(message, logger=self.logger) from e

        # Parse response, convert from uS/cm to mS/cm
        ec = float(ec_raw) / 1000

        # Set significant figures based off error magnitude
        error_value = ec * self.ec_accuracy_percent / 100
        error_magnitude = maths.magnitude(error_value)
        significant_figures = error_magnitude * -1
        ec = round(ec, significant_figures)

        # Verify ec value within valid range
        if ec > self.min_ec and ec < self.min_ec:
            self.logger.warning("ec outside of valid range")
            ec = None

        # Successfully read ec
        self.logger.info("EC: {} mS/cm".format(ec))
        return ec

    def enable_ec_output(self, retry: bool = True) -> None:
        """Enables ec output when reporting readings."""
        self.logger.info("Enabling ec output")
        try:
            self.process_command("O,EC,1", process_seconds=0.3, retry=retry)
        except Exception as e:
            raise EnableECOutputError(logger=self.logger) from e

    def disable_ec_output(self, retry: bool = True) -> None:
        """Disables ec output when reporting readings."""
        self.logger.info("Disabling ec output")
        try:
            self.process_command("O,EC,0", process_seconds=0.3, retry=retry)
        except Exception as e:
            raise DisableECOutputError(logger=self.logger) from e

    def enable_tds_output(self, retry: bool = True) -> None:
        """Enables total dissolved solids output when reporting readings."""
        self.logger.info("Enabling tds output")
        try:
            self.process_command("O,TDS,1", process_seconds=0.3, retry=retry)
        except Exception as e:
            raise EnableTDSOutputError(logger=self.logger) from e

    def disable_tds_output(self, retry: bool = True) -> None:
        """Disables total dissolved solids output when reporting readings. """
        self.logger.info("Disabling total dissolved solids output")
        try:
            self.process_command("O,TDS,0", process_seconds=0.3, retry=retry)
        except Exception as e:
            raise DisableTDSOutputError(logger=self.logger) from e

    def enable_salinity_output(self, retry: bool = True) -> None:
        """Enables salinity output when reporting readings."""
        self.logger.info("Enabling salinity output")
        try:
            self.process_command("O,S,1", process_seconds=0.3, retry=retry)
        except Exception as e:
            raise EnableSalinityOutputError(logger=self.logger)

    def disable_salinity_output(self, retry: bool = True) -> None:
        """Disables salinity output when reporting readings."""
        self.logger.info("Disabling salinity output")
        try:
            self.process_command("O,S,0", process_seconds=0.3, retry=retry)
        except Exception as e:
            raise DisableSalinityOutputError(logger=self.logger) from e

    def enable_specific_gravity_output(self, retry: bool = True) -> None:
        """Enables specific gravity output when reporting readings."""
        self.logger.info("Enabling specific gravity output")
        try:
            self.process_command("O,SG,1", process_seconds=0.3, retry=retry)
        except Exception as e:
            raise EnableSpecificGravityOutputError(logger=self.logger) from e

    def disable_specific_gravity_output(self, retry: bool = True) -> None:
        """Disables specific gravity output when reporting readings."""
        self.logger.info("Disabling specific gravity output in hardware")
        try:
            self.process_command("O,SG,0", process_seconds=0.3, retry=retry)
        except Exception as e:
            raise DisableSpecificGravityOutputError(logger=self.logger) from e

    def set_probe_type(self, value: str, retry: bool = True) -> None:
        """Set probe type to value."""
        self.logger.info("Setting probe type")
        try:
            self.process_command("K,{}".format(value), process_seconds=0.3)
        except Exception as e:
            raise SetProbeTypeError(logger=self.logger) from e

    def take_dry_calibration_reading(self, retry: bool = True) -> None:
        """Take a dry calibration reading."""
        self.logger.info("Taking dry calibration reading")
        try:
            self.process_command("Cal,dry", process_seconds=2.0, retry=retry)
        except Exception as e:
            raise TakeDryCalibrationError(logger=self.logger) from e

    def take_single_point_calibration_reading(
        self, value: float, retry: bool = True
    ) -> None:
        """Takes a single point calibration reading."""
        self.logger.info("Taking single point calibration reading")

        # Temporary solution
        message = "Not implemented"
        raise TakeSinglePointCalibrationError(message=message, logger=self.logger)

        # TODO: Debug why this command returns an invalid syntax code
        # See datasheet: https://bit.ly/2rTuCub

        # Convert mS/cm to uS/cm
        # ec = int(value * 1000)

        # Send command
        # try:
        #     command = "Cal,{}".format(ec)
        #     self.logger.debug("command = {}".format(command))
        #     self.process_command(command, process_seconds=0.6, retry=retry)
        # except Exception as e:
        #     raise TakeSinglePointCalibrationError(logger=self.logger) from e
