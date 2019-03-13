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
from device.peripherals.modules.actuator_grove_rgb_lcd import exceptions, simulator


class GroveRGBLCDDriver:
    """Driver for Grove RGB LCD display."""

    # --------------------------------------------------------------------------
    # Constants for Grove RBG LCD
    CMD = 0x80
    CLEAR = 0x01
    DISPLAY_ON_NO_CURSOR = 0x08 | 0x04
    TWO_LINES = 0x28
    CHAR = 0x40
    NEWLINE = 0xC0
    RGB_ADDRESS = 0x62
    LCD_ADDRESS = 0x3E

    # --------------------------------------------------------------------------
    def __init__(
        self,
        name: str,
        i2c_lock: threading.RLock,
        bus: int,
        rgb_address: int = RGB_ADDRESS,
        lcd_address: int = LCD_ADDRESS,
        mux: Optional[int] = None,
        channel: Optional[int] = None,
        simulate: bool = False,
        mux_simulator: Optional[MuxSimulator] = None,
    ) -> None:
        """Initializes Grove RGB LCD."""

        # Initialize logger
        logname = "GroveRGBLCD({})".format(name)
        self.logger = Logger(logname, __name__)

        # Check if simulating
        if simulate:
            self.logger.info("Simulating driver")
            Simulator = simulator.GroveRGBLCDSimulator
        else:
            Simulator = None

        # Initialize I2C
        try:
            self.i2c_rgb = I2C(
                name="RGB-{}".format(name),
                i2c_lock=i2c_lock,
                bus=bus,
                address=rgb_address,
                mux=mux,
                channel=channel,
                mux_simulator=mux_simulator,
                PeripheralSimulator=Simulator,
            )
            self.i2c_lcd = I2C(
                name="LCD-{}".format(name),
                i2c_lock=i2c_lock,
                bus=bus,
                address=lcd_address,
                mux=mux,
                channel=channel,
                mux_simulator=mux_simulator,
                PeripheralSimulator=Simulator,
            )
        except I2CError as e:
            raise exceptions.InitError(logger=self.logger) from e

        # Initialize the display
        try:
            # command: clear display
            self.i2c_lcd.write(bytes([self.CMD, self.CLEAR]))
            time.sleep(0.05)  # Wait for lcd to process

            # command: display on, no cursor
            self.i2c_lcd.write(bytes([self.CMD, self.DISPLAY_ON_NO_CURSOR]))

            # command: 2 lines
            self.i2c_lcd.write(bytes([self.CMD, self.TWO_LINES]))
            time.sleep(0.05)  # Wait for lcd to process

        except I2CError as e:
            raise exceptions.DriverError(logger=self.logger) from e

    # --------------------------------------------------------------------------
    def set_backlight(self, R: int = 0x00, G: int = 0x00, B: int = 0x00) -> None:
        """Turns on the LCD backlight at the level and color specified. 0 - 255 are valid inputs for RGB."""
        # validate the inputs are 0 <> 255
        if R < 0 or R > 255 or G < 0 or G > 255 or B < 0 or B > 255:
            self.logger.error("RGB values must be between 0 and 255")
            raise exceptions.DriverError(logger=self.logger)

        message = "Setting RGB backlight: {:2X}, {:2X}, {:2X}".format(R, G, B)
        self.logger.debug(message)

        # Set the backlight RGB value
        try:
            self.i2c_rgb.write(bytes([0, 0]))
            self.i2c_rgb.write(bytes([1, 0]))
            self.i2c_rgb.write(bytes([0x08, 0xAA]))
            self.i2c_rgb.write(bytes([4, R]))
            self.i2c_rgb.write(bytes([3, G]))
            self.i2c_rgb.write(bytes([2, B]))
        except I2CError as e:
            raise exceptions.DriverError(logger=self.logger) from e

    # --------------------------------------------------------------------------
    def write_string(self, message: str = "") -> None:
        """Writes a string to the LCD (16 chars per line limit, 2 lines). Use a '/n' newline character in the string to start the secone line."""
        self.logger.debug("Writing '{}' to LCD".format(message))
        try:
            # command: clear display
            self.i2c_lcd.write(bytes([self.CMD, self.CLEAR]))
            time.sleep(0.05)  # Wait for lcd to process
            for char in message:
                # write to the second line? (two lines max, not enforced)
                if char == "\n":
                    self.i2c_lcd.write(bytes([self.CMD, self.NEWLINE]))
                    continue
                # get the hex value of the char
                c = ord(char)
                self.i2c_lcd.write(bytes([self.CHAR, c]))
                # (there is a 16 char per line limit that I'm not enforcing)
        except I2CError as e:
            raise exceptions.DriverError(logger=self.logger) from e

    # --------------------------------------------------------------------------
    def display_time(self, retry: bool = True) -> None:
        """Clears LCD and displays current time."""
        # utc = time.gmtime()
        lt = time.localtime()
        now = "{}".format(time.strftime("%F %X", lt))
        self.logger.debug("Writing time {}".format(now))
        try:
            # command: clear display
            self.i2c_lcd.write(bytes([self.CMD, self.CLEAR]))
            time.sleep(0.05)  # Wait for lcd to process
            self.write_string(now)
        except exceptions.DriverError as e:
            raise exceptions.DriverError(logger=self.logger) from e
