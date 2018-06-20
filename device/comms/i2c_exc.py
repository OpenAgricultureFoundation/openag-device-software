# Import standard python libraries
import fcntl, io, time, logging, threading
from ctypes import *
import struct

# Import device utilities
from device.utilities.logger import Logger
from device.comms.utilities.i2c import *


class I2C(object):
    """ I2C communication device. Can communicate with device directly or 
        via an I2C mux. """

    # Initialize I2C communication options
    I2C_SLAVE = 0x0703 # Use this slave address
    I2C_RDWR = 0x0707  # Combined R/W transfer (one STOP only)
    I2C_M_RD = 0x0001  # read data, from slave to master


    def __init__(self, name: str, bus: int, address: int, mux: Optional[int] = None, 
        channel: Optional[int] = None, simulate: bool = False):
        """ Initialize I2C device. """

        # Initialize passed in parameters
        self.name = name
        self.bus = bus
        self.address = address
        self.mux = mux
        self.channel = channel
        self.simulate = simulate

        # Initialize logger instance
        logger_name = "I2C({})".format(self.name)
        self.logger = Logger(
            name = logger_name,
            dunder_name = __name__,
        )

        # Check if simulated
        if self.simulate:
            self.logger.debug("Simulated initialization")
            return

        # I2C not simulated, open device
        try:
            device_name = "/dev/i2c-{}".format(bus)
            self.device = io.open(device_name, "r+b", buffering=0)
        except PermissionError as e:
            raise InitializationError("Unable to open device: {}".format(device_name)) from e

        # Verify device exists by trying to detect device
        try:
            byte = self.read(1)
        except ReadError as e:
            raise InitializationError("Unable to detect device") from e

        # Initialization successful!
        self.logger.debug("Successfully initialized")


    def __del__(self):
        """Clean up any resources used by the I2c instance."""
        self.close()


    def __enter__(self):
        """Context manager enter function."""
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit function, ensures resources are cleaned up."""
        self.close()
        return False  # Don't suppress exceptions.


    def write(self, byte_list: List[int], retry=False):
        """ Writes byte list to device. Converts byte list to byte array then 
            sends bytes. Returns error message. """

        # Handle mux interactions
        self.set_mux()

        # Build byte array and string
        byte_array = bytearray(byte_list)
        byte_string = "".join('0x{:02X} '.format(b) for b in byte_array)

        # Check if i2c is simulated
        if self.simulate:
            self.logger.debug("Simulating writing: {}".format(byte_string))
            return

        # I2C is not simulated!
        try:
            with threading.Lock():
                self.logger.debug("Writing: {}".format(byte_string))
                fcntl.ioctl(self.device, self.I2C_SLAVE, self.address)
                self.device.write(byte_array)
        except IOError as e:
            raise WriteError(byte_list) from e


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


    def read_register(self, register_address, retry=False):
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


    @retry(MuxError, tries=5, delay=0.1, backoff=2, logger=self.logger)
    def set_mux(self):
        """ Sets mux to channel if enabled. """

        # Build byte array and string
        channel_byte = 0x01 << self.channel
        byte_list = [channel_byte]
        byte_array = bytearray(byte_list)
        byte_string = "".join('0x{:02X} '.format(b) for b in byte_array)

        # Check if mux is simulated
        if self.simulate:
            self.logger.debug("Simulating setting mux 0x{:02X} to channel {}, writing: 0x{:02X}".format(
            self.mux, self.channel, channel_byte))
            return

        # Mux is not simulated!
        try:
            with threading.Lock():
                self.logger.debug("Setting mux 0x{:02X} to channel {}, writing: 0x{:02X}".format(
                    self.mux, self.channel, channel_byte))
                fcntl.ioctl(self.device, self.I2C_SLAVE, self.mux)
                self.device.write(byte_array)
        except IOError as e:
            raise MuxError(self.mux, self.channel) from e


    def close(self):
        """ Closes device. """
        if not self.simulate:
            self.device.close()



def scan(address_range=None, mux_range=None, channel_range=None):
    """Scan for devices at specified address, mux, and channel ranges."""
    ...


class I2CError(Exception):
    """Base class for errors raised by I2C."""


class InitializationError(I2CError):
    """Exception raised for initialization errors.

    Attributes:
        message -- explanation of the error
        i2c -- instance of I2C object trying to be initialized
    """

    def __init__(self, message):
        self.message = message


class ReadError(I2CError):
    """Exception raised for read errors."""


class WriteError(I2CError):
    """Exception raised for write errors."""

     def __init__(self, message, byte_list, ):
        self.message = message


class MuxError(I2CError):
    """Exception raised for write errors."""



def retry(exceptions, tries=5, delay=0.1, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    Args:
        exceptions: The exception to check. may be a tuple of
            exceptions to check.
        tries: Number of times to try (not retry) before giving up.
        delay: Initial delay between retries in seconds.
        backoff: Backoff multiplier (e.g. value of 2 will double the delay
            each retry).
        logger: Logger to use. If None, print.
    """
    
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return = f(*args, **kwargs)
                except exceptions as e:

                    msg = '{}, Retrying in {} seconds...'.format(e, mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry