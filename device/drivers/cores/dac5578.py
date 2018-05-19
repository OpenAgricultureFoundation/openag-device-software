# Import standard python modules
import time, threading
from typing import Optional, Tuple

# Import driver parent class
from device.drivers.classes.i2c_driver_core import I2CDriverCore

# Import device utilities
from device.utilities import bitwise


class DAC5578Core(I2CDriverCore):
    """ Driver core for DAC5578 digital to analog converter. """

    def __init__(self, name: str, bus: int, address: int, mux: Optional[int] = None, 
                channel: Optional[int] = None, simulate: bool = False) -> None:
        """ Initializes DAC5578 Core. """

        # Initialize parent class
        super().__init__(
            name = name, 
            bus = bus, 
            address = address, 
            mux = mux, 
            channel = channel, 
            simulate = simulate,
            i2c_name = "DAC5578-{}".format(name),
            logger_name = "DAC5578Core({})".format(name),
            dunder_name = __name__,
        )


    def set_outputs(self, outputs: dict) -> Optional[str]:
        """ Sets output channels to output percents. Only sets mux once. 
            Keeps thread locked since relies on mux not changing. """
        self.logger.debug("Setting outputs: {}".format(outputs))

        # Run through each output
        first = True
        for channel, percent in outputs:

            # Lock thread since we rely on mux not changing
            with threading.Lock():

                # Only set mux once
                if first:
                    error = self.set_output(channel, percent)
                    first = False
                else:
                    error = self.set_output(channel, percent, disable_mux=True)

                # Check for errors
                if error != None:
                    self.logger.error("Unable to set outputs")
                    return error

        # Successfully set outputs
        self.logger.debug("Successfully set outputs")
        return None


    def set_output(self, channel: int, percent: int, disable_mux: bool = False) -> Optional[str]:
        """ Sets output value to channel. """
        self.logger.debug("Setting output on channel {} to: {}%".format(channel, percent))

        # Check valid channel range
        if channel < 0 or channel > 7:
            return "Channel out of range, must be within 0-7"

        # Check valid value range
        if percent < 0 or percent > 100:
            return "Output percent out of range, must be within 0-100"

        # Convert output percent to byte
        byte = 255 - int(percent * 2.55) # 255 is off, 0 is on

        # Send set output command to dac
        self.logger.debug("Writing to dac: ch={}, byte={}".format(channel, byte))
        error = self.i2c.write([0x30+channel, byte, 0x00], disable_mux=disable_mux)

        # Check for errors
        if error != None:
            self.logger.error("Unable to set output")
            return error

        # Successfully set output
        self.logger.debug("Successfully set output")
        return None


    def read_power_register(self) -> Tuple[Optional[dict], Optional[str]]:
        """ Reads power register. """
        self.logger.debug("Reading power register")

        # Read power down register
        # TODO: Do we need to lock thread here? or block read?
        self.i2c.write([0x40])
        byte_array, error = self.i2c.read(2)

        # Check for errors
        if error != None:
            self.logger.error("Unable to read power register")
            return None, error

        # Successfully read register!
        msb = byte_array[0]
        lsb = byte_array[1]
        powered = {
            0: not bool(bitwise.get_bit_from_byte(4, msb)),
            1: not bool(bitwise.get_bit_from_byte(3, msb)),
            2: not bool(bitwise.get_bit_from_byte(2, msb)),
            3: not bool(bitwise.get_bit_from_byte(1, msb)),
            4: not bool(bitwise.get_bit_from_byte(0, msb)),
            5: not bool(bitwise.get_bit_from_byte(7, lsb)),
            6: not bool(bitwise.get_bit_from_byte(6, lsb)),
            7: not bool(bitwise.get_bit_from_byte(5, lsb)),
        }
        self.logger.debug("Successfully read power register, powered={}".format(powered))
        return powered, error
