# Import standard python modules
import time, threading

# Import python types
from typing import NamedTuple, Optional, Dict

# Import device comms
from device.comms.i2c2.main import I2C
from device.comms.i2c2.exceptions import I2CError
from device.comms.i2c2.mux_simulator import MuxSimulator

# Import device utilities
from device.utilities.logger import Logger
from device.utilities import bitwise

# Import driver elements
from device.peripherals.common.dac5578.simulator import DAC5578Simulator

# Import exceptions
from device.peripherals.classes.peripheral.exceptions import InitError
from device.peripherals.common.dac5578.exceptions import (
    WriteOutputError,
    WriteOutputsError,
    ReadPowerRegisterError,
    SetHighError,
    SetLowError,
)


class DAC5578Driver:
    """Driver for DAC5578 digital to analog converter."""

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
        """Initializes DAC5578."""

        # Initialize logger
        self.logger = Logger(name="DAC5578-({})".format(name), dunder_name=__name__)

        # Check if simulating
        if simulate:
            self.logger.info("Simulating driver")
            Simulator = DAC5578Simulator
        else:
            Simulator = None

        # Initialize I2C
        try:
            self.i2c = I2C(
                name="DAC5578-{}".format(name),
                bus=bus,
                address=address,
                mux=mux,
                channel=channel,
                mux_simulator=mux_simulator,
                PeripheralSimulator=Simulator,
            )
        except I2CError as e:
            raise InitError(logger=self.logger) from e

    def write_output(
        self, channel: int, percent: int, retry: bool = True, disable_mux: bool = False
    ) -> None:
        """Sets output value to channel."""
        message = "Writing output on channel {} to: {}%".format(channel, percent)
        self.logger.debug(message)

        # Check valid channel range
        if channel < 0 or channel > 7:
            message = "channel out of range, must be within 0-7"
            raise WriteOutputError(message=message, logger=self.logger)

        # Check valid value range
        if percent < 0 or percent > 100:
            message = "output percent out of range, must be within 0-100"
            raise WriteOutputError(message=message, logger=self.logger)

        # Convert output percent to byte, ensure 100% is byte 255
        if percent == 100:
            byte = 255
        else:
            byte = int(percent * 2.55)

        # Send set output command to dac
        self.logger.debug("Writing to dac: ch={}, byte={}".format(channel, byte))
        try:
            self.i2c.write([0x30 + channel, byte, 0x00], disable_mux=disable_mux)
        except I2CError as e:
            raise WriteOutputError(logger=self.logger) from e

    def write_outputs(self, outputs: dict, retry: bool = True) -> None:
        """Sets output channels to output percents. Only sets mux once. 
        Keeps thread locked since relies on mux not changing."""
        self.logger.debug("Writing outputs: {}".format(outputs))

        # Check output dict is not empty
        if len(outputs) < 1:
            message = "output dict must not be empty"
            raise WriteOutputsError(message=message, logger=self.logger)

        if len(outputs) > 8:
            print("outputs len = {}".format(len(outputs)))
            message = "output dict must not contain more than 8 entries"
            raise WriteOutputsError(message=message, logger=self.logger)

        # Run through each output
        for channel, percent in outputs.items():
            message = "Writing output for ch {}: {}%".format(channel, percent)
            self.logger.debug(message)
            try:
                self.write_output(channel, percent, retry=retry)
            except WriteOutputError as e:
                raise WriteOutputsError(logger=self.logger) from e

    def read_power_register(self, retry: bool = True) -> Optional[Dict[int, bool]]:
        """Reads power register."""
        self.logger.debug("Reading power register")

        # Read register
        try:
            self.i2c.write([0x40], retry=retry)
            bytes_ = self.i2c.read(2, retry=retry)
        except I2CError as e:
            raise ReadPowerRegisterError(logger=self.logger) from e

        # Parse response bytes
        msb = bytes_[0]
        lsb = bytes_[1]
        powered_channels = {
            0: not bool(bitwise.get_bit_from_byte(4, msb)),
            1: not bool(bitwise.get_bit_from_byte(3, msb)),
            2: not bool(bitwise.get_bit_from_byte(2, msb)),
            3: not bool(bitwise.get_bit_from_byte(1, msb)),
            4: not bool(bitwise.get_bit_from_byte(0, msb)),
            5: not bool(bitwise.get_bit_from_byte(7, lsb)),
            6: not bool(bitwise.get_bit_from_byte(6, lsb)),
            7: not bool(bitwise.get_bit_from_byte(5, lsb)),
        }
        return powered_channels

    def set_high(self, channel: Optional[int] = None, retry: bool = True) -> None:
        """Sets channel high, sets all channels high if no channel is specified."""
        if channel != None:
            self.logger.debug("Setting channel {} high".format(channel))
            try:
                self.write_output(channel, 100, retry=retry)  # type: ignore
            except WriteOutputError as e:
                raise SetHighError(logger=self.logger) from e
        else:
            self.logger.debug("Setting all channels high")
            outputs = {0: 100, 1: 100, 2: 100, 3: 100, 4: 100, 5: 100, 6: 100, 7: 100}
            try:
                self.write_outputs(outputs, retry=retry)
            except WriteOutputsError as e:
                raise SetHighError(logger=self.logger) from e

    def set_low(self, channel: Optional[int] = None, retry: bool = True) -> None:
        """Sets channel low, sets all channels low if no channel is specified."""
        if channel != None:
            self.logger.debug("Setting channel {} low".format(channel))
            try:
                self.write_output(channel, 100, retry=retry)  # type: ignore
            except WriteOutputError as e:
                raise SetLowError(logger=self.logger) from e
        else:
            self.logger.debug("Setting all channels low")
            outputs = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
            try:
                self.write_outputs(outputs, retry=retry)
            except WriteOutputsError as e:
                raise SetLowError(logger=self.logger) from e

    # def probe(self) -> Error:
    #     """Probes dac5578 by trying to read the power register."""
    #     self.logger.debug("Probing")
    #     powered, error = self.read_power_register()
    #     if error.exists():
    #         error.report("DAC probe failed")
    #         self.logger.error(error.latest())
    #         return error
    #     else:
    #         return Error(None)
