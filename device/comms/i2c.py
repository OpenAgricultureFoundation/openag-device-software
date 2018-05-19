# Import standard python libraries
import fcntl, io, time, logging, threading
from ctypes import *
import struct

# Import device utilities
from device.utilities.logger import Logger


# TODO: test if atlas sensors work with single file manager
# TODO: add more descriptive error messages


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


        # extra = {'console_name':logger_name, 'file_name': logger_name}
        # logger = logging.getLogger(__name__)
        # self.logger = logging.LoggerAdapter(logger, extra)

        # Initialize file managers
        if not self.simulate:
            self.fr = io.open("/dev/i2c-" + str(bus), "rb", buffering=0)
            self.fw = io.open("/dev/i2c-" + str(bus), "wb", buffering=0)
            self.frw = io.open("/dev/i2c-" + str(bus), "r+b", buffering=0)


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

        # Verify byte list is a list
        if type(byte_list) != list:
            raise ValueError("byte_list must be a list")

        # Verify byte list is a list of ints
        if type(byte_list[0]) != int:
            raise ValueError("byt_list must be a list of ints")

        # Handle mux interactions
        error = self.manage_mux(disable_mux=disable_mux)

        # Check for mux error
        if error != None:
            return error

        # Build byte array and string
        byte_array = bytearray(byte_list)
        byte_string = "".join('0x{:02X} '.format(b) for b in byte_array)

        # Check if i2c is simulated
        if self.simulate:
            self.logger.debug("Simulating writing: {}".format(byte_string))
            return None

        # I2c is not simulated!
        try:
            with threading.Lock():
                self.logger.debug("Writing: {}".format(byte_string))
                fcntl.ioctl(self.fw, self.I2C_SLAVE, self.address)
                self.fw.write(byte_array)
                return None
        except:
            return "Write failed" # TODO: handle specific exceptions


    def write_raw(self, bytes_, disable_mux=False):
        """ Writes raw bytes to device. """

        # Handle mux interactions
        error = self.manage_mux(disable_mux=disable_mux)

        # Check for mux error
        if error != None:
            return error

        # Check if i2c is simulated
        if self.simulate:
            self.logger.debug("Simulating writing: {}".format(bytes_))
            return None

        # I2c is not simulated!
        try:
            with threading.Lock():
                self.logger.debug("Writing: {}".format(bytes_))
                fcntl.ioctl(self.fw, self.I2C_SLAVE, self.address)
                self.fw.write(bytes)
                return None
        except:
            return "Write raw failed" # TODO: handle specific exceptions


    def read(self, num_bytes, disable_mux=False):
        """ Reads num bytes from device. Returns byte array. """
        self.logger.debug("Reading {} bytes".format(num_bytes))

        # Handle mux interactions
        error = self.manage_mux(disable_mux=disable_mux)

        # Check for mux error
        if error != None:
            return None, error

        # Check if i2c is simulated
        if self.simulate:
            byte_array = bytearray(num_bytes)
            byte_string = "".join('0x{:02X} '.format(b) for b in byte_array)
            self.logger.debug("Simulated read: {}".format(byte_string))
            return byte_array, None

        # I2c is not simulated!
        try:
            with threading.Lock():
                fcntl.ioctl(self.fr, self.I2C_SLAVE, self.address)
                raw_bytes = self.fr.read(num_bytes)
                byte_array = bytearray(raw_bytes)
                byte_string = "".join('0x{:02X} '.format(b) for b in byte_array)
                self.logger.debug("Read: {}".format(byte_string))
                return byte_array, None
        except:
            return None, "Read failed" # TODO: handle specific exceptions


    def read_raw(self, num_bytes, disable_mux=False):
        """ Reads num bytes from device. Returns raw bytes. """

        # Handle mux interactions
        error = self.manage_mux(disable_mux=disable_mux)

        # Check for mux error
        if error != None:
            return None, error

        # Check if i2c is simulated
        if self.simulate:
            bytes_ = bytes(num_bytes)
            self.logger.debug("Simulated read raw: {}".format(bytes_))
            return bytes_, None

        # I2c is not simulated!
        try:
            with threading.Lock():
                self.fr = io.open("/dev/i2c-" + str(bus), "rb", buffering=0)
                bytes_ = self.fr.read(num_bytes)
                self.logger.debug("Read raw: {}".format(bytes_))
                return bytes_, None
        except:
            return None, "Read raw failed" # TODO: handle specific exceptions


    def read_register(self, register_address, disable_mux=False):
        """ Reads byte stored in register at address. """
        
        # Handle mux interactions
        error = self.manage_mux(disable_mux=disable_mux)

        # Check for mux error
        if error != None:
            return None, error

        # Check if i2c is simulated
        if self.simulate:
            byte_ = bytes(1)[0]
            self.logger.debug("Simulated read register: {}".format(byte_))
            return byte_, None

        # I2c is not simulated!
        try:
            with threading.Lock():
                reg = c_uint8(register_address)
                result = c_uint8()
                request = self.make_i2c_rdwr_data([
                    (self.address, 0, 1, pointer(reg)), # write cmd register
                    (self.address, self.I2C_M_RD, 1, pointer(result)) # read 1 byte as result
                ])
                fcntl.ioctl(self.frw.fileno(), self.I2C_RDWR, request)
                byte_ = result.value
                self.logger.debug("Read register: {}".format(byte_))
                return byte_, None
        except:
            return None, "Read register failed" # TODO: handle specific exceptions


    def manage_mux(self, disable_mux=False):
        """ Sets mux to channel if enabled. """

        # Check if mux requires update
        if not self.mux_enabled or disable_mux:
            return None

        # Build byte array and string
        channel_byte = 0x01 << self.channel
        byte_list = [channel_byte]
        byte_array = bytearray(byte_list)
        byte_string = "".join('0x{:02X} '.format(b) for b in byte_array)

        # Check if mux is simulated
        if self.simulate:
            self.logger.debug("Simulating setting mux 0x{:02X} to channel {}, writing: 0x{:02X}".format(
            self.mux, self.channel, channel_byte))
            return None

        # Mux is not simulated!
        try:
            with threading.Lock():
                self.logger.debug("Setting mux 0x{:02X} to channel {}, writing: 0x{:02X}".format(
                    self.mux, self.channel, channel_byte))
                fcntl.ioctl(self.fw, self.I2C_SLAVE, self.mux)
                self.fw.write(byte_array)
        except:
            return "Manage mux failed" # TODO: handle specific exceptions


    def close(self):
        """ Closes device. """
        if not self.simulate:
            self.fw.close()
            self.fr.close()
            self.frw.close()


################################# Helper Functions ############################


    def make_i2c_rdwr_data(self, messages):
        """Utility function to create and return an i2c_rdwr_ioctl_data structure
        populated with a list of specified I2C messages.  The messages parameter
        should be a list of tuples which represent the individual I2C messages to
        send in this transaction.  Tuples should contain 4 elements: address value,
        flags value, buffer length, ctypes c_uint8 pointer to buffer.
        """
        # Create message array and populate with provided data.
        msg_data_type = i2c_msg*len(messages)
        msg_data = msg_data_type()
        for i, m in enumerate(messages):
            msg_data[i].addr  = m[0] & 0x7F
            msg_data[i].flags = m[1]
            msg_data[i].len   = m[2]
            msg_data[i].buf   = m[3]
        # Now build the data structure.
        data = i2c_rdwr_ioctl_data()
        data.msgs  = msg_data
        data.nmsgs = len(messages)
        return data


############################# Data Classes ####################################
    

class i2c_msg(Structure):
    _fields_ = [
        ('addr',  c_uint16),
        ('flags', c_uint16),
        ('len',   c_uint16),
        ('buf',   POINTER(c_uint8))
    ]


class i2c_rdwr_ioctl_data(Structure):
    _fields_ = [
        ('msgs',  POINTER(i2c_msg)),
        ('nmsgs', c_uint32)
    ]