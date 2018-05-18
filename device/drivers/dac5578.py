# Import standard python modules
import time
from typing import Optional, Tuple

# Import driver parent class
from device.drivers.classes.i2c_driver import I2CDriver

# Import device utilities
from device.utilities import bitwise


class DAC5578(I2CDriver):
    """ Driver for DAC5578 digital to analog converter. """


    def set_output(self, channel: int, percent: int) -> Optional[str]:
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
        self.logger.debug("Writing to dac5578({}): ch={}, byte={}".format(self.name, channel, byte))
        error = self.i2c.write([0x30+channel, percent, 0x00])

        # Check for errors
        if error != None:
            self.logger.error("Unable to set output on dac5578({})".format(self.name))
            self.health.report_failure()
            return error

        # Successfully set output
        self.logger.debug("Successfully set output on dac5578({})")
        self.health.report_success()
        return error


    def get_status(self) -> Tuple[Optional[Status], Optional[str]]:
        """ Gets device status by reading power down register. """
        self.logger.debug("Getting status from dac5578({})".format(self.name))

        # Read power down register
        # TODO: Do we need to lock thread here? or block read?
        self.i2c.write([0x40])
        byte_array, error = self.i2c.read(2)

        # Check for errors
        if error != None:
            self.logger.debug("Unable to get status from dac5578({})".format(self.name))
            self.health.report_failure()
            return None, error

        # Successfully read status!
        msb = byte_array[0]
        lsb = byte_array[1]
        status = Status(
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
        )
        self.logger.debug("Successfully read status from dac5578({}), status={}".format(self.name, status))
        self.health.report_success()
        return status, error



# class Status(NamedTuple):
#     powered: list

class Status:
    """ Dataclass for dac5578 status. """

    def __init__(self, powered):
        self.powered = powered

    def __str__(self):
        return "Status(powered={})".format(self.powered)