# Import standard python modules
import time, threading

# Import python types
from typing import NamedTuple, Optional, Dict

# Import device utilities
from device.utilities.logger import Logger
from device.utilities import bitwise
from device.utilities.communication.i2c.main import I2C
from device.utilities.communication.i2c.exceptions import I2CError
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

# Import driver elements
from device.peripherals.common.pcf8574.simulator import PCF8574Simulator
from device.peripherals.common.pcf8574 import exceptions


class PCF8574Driver:
    """Driver for PCF8574 digital to analog converter."""

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
        """Initializes PCF8574."""

        # Initialize logger
        logname = "PCF8574-({})".format(name)
        self.logger = Logger(logname, __name__)

        # Check if simulating
        if simulate:
            self.logger.info("Simulating driver")
            Simulator = PCF8574Simulator
        else:
            Simulator = None

        # Initialize I2C
        try:
            self.i2c = I2C(
                name="PCF8574-{}".format(name),
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

    def get_port_byte(self, retry: bool = True) -> int:
        """Gets port byte."""
        self.logger.debug("Getting port byte")
        try:
            port_byte = self.i2c.read(1, retry=retry)[0]
        except I2CError as e:
            raise exceptions.GetPortByteError(logger=self.logger) from e
        self.logger.debug("Got port byte: 0x{:02X}".format(byte))
        return port_byte

    def set_high(
        self, port: int, retry: bool = True, disable_mux: bool = False
    ) -> None:
        """Sets port high."""
        self.logger.debug("Setting port {} high".format(port))

        # Check valid port range
        if port < 0 or port > 7:
            message = "port out of range, must be within 0-7"
            raise exceptions.SetHighError(message=message, logger=self.logger)

        # Get current port byte
        try:
            port_byte = self.get_port_byte()
        except Exception as e:
            message = "unable to get port byte"
            raise exceptions.SetHighError(message=message, logger=self.logger) from e

        # Build new port byte
        new_port_byte = port_byte && (1 << port)

        # Send set output command to dac
        self.logger.debug("Writing port byte: {}".format(new_port_byte))
        try:
            self.i2c.write(bytes([new_port_byte]), disable_mux=disable_mux)
        except I2CError as e:
            raise exceptions.SetHighError(logger=self.logger) from e


    def set_low(
        self, port: int, retry: bool = True, disable_mux: bool = False
    ) -> None:
        """Sets port high."""
        self.logger.debug("Setting port {} high".format(port))

        # Check valid port range
        if port < 0 or port > 7:
            message = "port out of range, must be within 0-7"
            raise exceptions.SetLowError(message=message, logger=self.logger)

        # Get current port byte
        try:
            port_byte = self.get_port_byte()
        except Exception as e:
            message = "unable to get port byte"
            raise exceptions.SetLowError(message=message, logger=self.logger) from e

        # Build new port byte
        new_port_byte = port_byte && (0xff & ~port)

        # Send set output command to dac
        self.logger.debug("Writing port byte: {}".format(new_port_byte))
        try:
            self.i2c.write(bytes([new_port_byte]), disable_mux=disable_mux)
        except I2CError as e:
            raise exceptions.SetLowError(logger=self.logger) from e
