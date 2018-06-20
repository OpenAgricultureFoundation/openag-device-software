# Import standard python modules
import time, threading
from typing import Optional, Tuple

# Import device comms
from device.comms.i2c import I2C

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error
from device.utilities import bitwise


class DAC5578:
    """ Driver for DAC5578 digital to analog converter. """

    def __init__(self, name: str, bus: int, address: int, mux: Optional[int] = None, 
                channel: Optional[int] = None, simulate: bool = False) -> None:
        """ Initializes DAC5578. """

        # Initialize parameters
        self.simulate = simulate

        # Initialize logger
        self.logger = Logger(
            name = "DAC5578-({})".format(name),
            dunder_name = __name__,
        )

        # Initialize I2C
        self.i2c = I2C(
            name = "DAC5578-{}".format(name),
            bus = bus,
            address = address,
            mux = mux,
            channel = channel,
            simulate = simulate,
        )


    def write_output(self, channel: int, percent: int, disable_mux: bool = False) -> Error:
        """ Sets output value to channel. """
        self.logger.debug("Writing output on channel {} to: {}%".format(channel, percent))

        # Check valid channel range
        if channel < 0 or channel > 7:
            raise ValueError("Channel out of range, must be within 0-7")

        # Check valid value range
        if percent < 0 or percent > 100:
            raise ValueError("Output percent out of range, must be within 0-100")

        # Convert output percent to byte
        byte = 255 - int(percent * 2.55) # 255 is off, 0 is on

        # Send set output command to dac
        self.logger.debug("Writing to dac: ch={}, byte={}".format(channel, byte))
        error = self.i2c.write([0x30+channel, byte, 0x00], disable_mux=disable_mux)

        # Check for errors
        if error.exists():
            error.report("DAC unable to write output")
            self.logger.error(error.summary())
            return error

        # Successfully wrote output
        self.logger.debug("Successfully wrote output")
        return Error(None)


    def write_outputs(self, outputs: dict, retries=1) -> Error:
        """ Sets output channels to output percents. Only sets mux once. 
            Keeps thread locked since relies on mux not changing. """
        self.logger.debug("Writing outputs: {}".format(outputs))

        # Run through each output
        first = True
        for channel, percent in outputs.items():

            # Loop for retry option
            while True:

                # Write output
                error = self.write_output(channel, percent)

                # Check for success
                if not error.exists():
                    return Error(None)

                # Handle errors
                error.report("DAC unable to write outputs")
                self.logger.error(error.summary())

                # Check for end of retry
                if retries < 1:
                    return error

                # Retry
                self.logger.debug("Retrying to write output")

                retries = retries-1
                time.sleep(0.2) # wait 200ms between retries

        # Successfully wrote outputs
        self.logger.debug("Successfully wrote outputs")
        return Error(None)


    def read_power_register(self) -> Tuple[Optional[dict], Error]:
        """ Reads power register. """
        self.logger.debug("Reading power register")

        # Send start read command
        error = self.i2c.write([0x40])

        # Check for errors
        if error.exists():
            error.report("Dac unable to read power register")
            self.logger.debug(error)
            return None, error

        # Read 2 bytes
        bytes_, error = self.i2c.read(2)

        # Check for errors
        if error.exists():
            error.report("DAC unable to read power register")
            self.logger.error(error.summary())
            return None, error

        # Successfully read register!
        msb = bytes_[0]
        lsb = bytes_[1]
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
        return powered, Error(None)


    def probe(self) -> Error:
        """ Probes dac5578 by trying to read the power register. """
        self.logger.debug("Probing")
        powered, error = self.read_power_register()
        if error.exists():
            error.report("DAC probe failed")
            self.logger.error(error.latest())
            return error
        else:
            return Error(None)


    def turn_on(self, channel: Optional[int] = None) -> Error:
        """ Turns on all channels if no channel is specified. """

        # Set channel or channels
        if channel != None:
            self.logger.debug("Turning on channel {}".format(channel))
            error = self.write_output(channel, 100)
        else:
            self.logger.debug("Turning on all channels")
            outputs = {0: 100, 1: 100, 2: 100, 3: 100, 4: 100, 5: 100, 6: 100, 7: 100}
            error = self.write_outputs(outputs)

        # Check for errors
        if error.exists():
            error.report("DAC unable to turn on")
            self.logger.error(error.latest())
            return error
        else:
            return Error(None)


    def turn_off(self, channel: Optional[int] = None) -> Error:
        """ Turns on all channels if no channel is specified. """

        # Set channel or channels
        if channel != None:
            self.logger.debug("Turning off channel {}".format(channel))
            error = self.write_output(channel, 0)
        else:
            self.logger.debug("Turning off all channels")
            outputs = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
            error = self.write_outputs(outputs)

        # Check for errors
        if error.exists():
            error.report("DAC unable to turn off")
            self.logger.error(error.latest())
            return error
        else:
            return Error(None)
