# Import standard python libraries
import fcntl, io, time, logging, threading
from ctypes import *
import struct

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error
from device.comms.utilities.i2c import *


# TODO: Handle more exception types / report smarter error messages


class I2C(object):
    """ I2C communication device. Can communicate with device directly or 
        via an I2C mux. """

    # Initialize I2C communication options
    I2C_SLAVE = 0x0703 # Use this slave address
    I2C_RDWR = 0x0707  # Combined R/W transfer (one STOP only)
    I2C_M_RD = 0x0001  # read data, from slave to master


    def __init__(self, name, bus, address, mux=None, channel=None, simulate=False):
        """ Initialize I2C device. """

        # Initialize passed in parameters
        self.name = name
        self.bus = bus
        self.address = address
        self.mux = mux
        self.channel = channel
        self.simulate = simulate

        # Initialize mux enabled paramter
        self.mux_enabled = (mux != None) and (channel != None)

        # Initialize logger instance
        logger_name = "I2C({})".format(self.name)
        self.logger = Logger(
            name = logger_name,
            dunder_name = __name__,
        )

        # Initialize file managers
        if not self.simulate:
            self.device = io.open("/dev/i2c-" + str(bus), "r+b", buffering=0)


    def __del__(self):
        """Clean up any resources used by the I2c instance."""
        self.close()


    def __enter__(self):
        """Context manager enter function."""
        # Just return this object so it can be used in a with statement, like
        # with I2C(..) as i2c:
        #     # do stuff!
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit function, ensures resources are cleaned up."""
        self.close()
        return False  # Don't suppress exceptions.


    def write(self, byte_list, disable_mux=False):
        """ Writes byte list to device. Converts byte list to byte array then 
            sends bytes. Returns error message. """

        # TODO: remove type checks since static type checking should handle this

        # Verify byte list is a list
        if type(byte_list) != list:
            raise ValueError("byte_list must be a list")

        # Verify byte list is a list of ints
        if type(byte_list[0]) != int:
            raise ValueError("byt_list must be a list of ints")

        # Handle mux interactions
        error = self.manage_mux(disable_mux=disable_mux)

        # Check for mux error
        if error.exists():
            error.report("I2C write failed")
            return error

        # Build byte array and string
        byte_array = bytearray(byte_list)
        byte_string = "".join('0x{:02X} '.format(b) for b in byte_array)

        # Check if i2c is simulated
        if self.simulate:
            self.logger.debug("Simulating writing: {}".format(byte_string))
            return Error(None)

        # I2c is not simulated!
        try:
            with threading.Lock():
                self.logger.debug("Writing: {}".format(byte_string))
                fcntl.ioctl(self.device, self.I2C_SLAVE, self.address)
                self.device.write(byte_array)
                return Error(None)
        except IOError:
            error = Error("I2C write failed due to IO error")
            return error


    def write_raw(self, bytes_, disable_mux=False):
        """ Writes raw bytes to device. """

        # Handle mux interactions
        error = self.manage_mux(disable_mux=disable_mux)

        # Check for mux error
        if error.exists():
            error.report("I2C unable to write raw")
            return error

        # Check if i2c is simulated
        if self.simulate:
            self.logger.debug("Simulating writing: {}".format(bytes_))
            return Error(None)

        # I2c is not simulated!
        try:
            with threading.Lock():
                self.logger.debug("Writing: {}".format(bytes_))
                fcntl.ioctl(self.device, self.I2C_SLAVE, self.address)
                self.device.write(bytes_)
                return Error(None)
        except IOError:
            return Error("I2C unable to write raw due to IO error")


    def read(self, num_bytes, disable_mux=False):
        """ Reads num bytes from device. Returns byte array. """
        self.logger.debug("Reading {} bytes".format(num_bytes))

        # Handle mux interactions
        error = self.manage_mux(disable_mux=disable_mux)

        # Check for mux error
        if error.exists():
            error.report("I2C unable to read")
            return None, error

        # Check if i2c is simulated
        if self.simulate:
            byte_array = bytearray(num_bytes)
            byte_string = "".join('0x{:02X} '.format(b) for b in byte_array)
            self.logger.debug("Simulated read: {}".format(byte_string))
            return byte_array, Error(None)

        # I2c is not simulated!
        try:
            with threading.Lock():
                fcntl.ioctl(self.device, self.I2C_SLAVE, self.address)
                raw_bytes = self.device.read(num_bytes)
                byte_array = bytearray(raw_bytes)
                byte_string = "".join('0x{:02X} '.format(b) for b in byte_array)
                self.logger.debug("Read: {}".format(byte_string))
                return byte_array, Error(None)
        except IOError:
            return None, Error("I2C unable to read due to IO error")


    def read_raw(self, num_bytes, disable_mux=False):
        """ Reads num bytes from device. Returns raw bytes. """

        # Handle mux interactions
        error = self.manage_mux(disable_mux=disable_mux)

        # Check for mux error
        if error.exists():
            error.report("I2C unable to read raw")
            return None, error

        # Check if i2c is simulated
        if self.simulate:
            bytes_ = bytes(num_bytes)
            self.logger.debug("Simulated read raw: {}".format(bytes_))
            return bytes_, Error(None)

        # I2c is not simulated!
        try:
            with threading.Lock():

                # TODO: Why are we opening this?
                self.device = io.open("/dev/i2c-" + str(bus), "rb", buffering=0)
                bytes_ = self.device.read(num_bytes)
                self.logger.debug("Read raw: {}".format(bytes_))
                return bytes_, Error(None)
        except IOError:
            return None, Error("I2C unable to read raw due to IO error")


    def read_register(self, register_address, disable_mux=False):
        """ Reads byte stored in register at address. """
        
        # Handle mux interactions
        error = self.manage_mux(disable_mux=disable_mux)

        # Check for mux error
        if error.exists():
            error.report("I2C unable to read register")
            return None, error

        # Check if i2c is simulated
        if self.simulate:
            byte_ = bytes(1)[0]
            self.logger.debug("Simulated read register: {}".format(byte_))
            return byte_, Error(None)

        # I2c is not simulated!
        try:
            with threading.Lock():
                reg = c_uint8(register_address)
                result = c_uint8()
                request = make_i2c_rdwr_data([
                    (self.address, 0, 1, pointer(reg)), # write cmd register
                    (self.address, self.I2C_M_RD, 1, pointer(result)) # read 1 byte as result
                ])
                fcntl.ioctl(self.device.fileno(), self.I2C_RDWR, request)
                byte_ = result.value
                self.logger.debug("Read register: {}".format(byte_))
                return byte_, Error(None)
        except IOError:
            return None, Error("I2C unable to read register due to IO error")


    def manage_mux(self, disable_mux=False):
        """ Sets mux to channel if enabled. """

        # Check if mux requires update
        if not self.mux_enabled or disable_mux:
            return Error(None)

        # Build byte array and string
        channel_byte = 0x01 << self.channel
        byte_list = [channel_byte]
        byte_array = bytearray(byte_list)
        byte_string = "".join('0x{:02X} '.format(b) for b in byte_array)

        # Check if mux is simulated
        if self.simulate:
            self.logger.debug("Simulating setting mux 0x{:02X} to channel {}, writing: 0x{:02X}".format(
            self.mux, self.channel, channel_byte))
            return Error(None)

        # Mux is not simulated!
        try:
            with threading.Lock():
                self.logger.debug("Setting mux 0x{:02X} to channel {}, writing: 0x{:02X}".format(
                    self.mux, self.channel, channel_byte))
                fcntl.ioctl(self.device, self.I2C_SLAVE, self.mux)
                self.device.write(byte_array)
                return Error(None)
        except IOError:
            return Error("I2C unable to set mux due to IO error")


    def close(self):
        """ Closes device. """
        if not self.simulate:
            self.device.close()
