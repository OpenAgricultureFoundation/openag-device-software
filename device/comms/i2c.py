# Import standard python libraries
import fcntl, io, time, logging


class I2C(object):
    """ I2C communication device. Can communicate with device directly or 
        via an I2C mux. """

    # Initialize I2C communication options
    I2C_SLAVE = 0x0703
    I2C_RDWR = 0x0707  # Combined R/W transfer (one STOP only)


    def __init__(self, bus, address, mux=None, channel=None):
        """ Initialize I2C device. """

        # Initialize standard i2c parameters
        self.bus = bus
        self.address = address

        # Initialize i2c mux parameters
        if mux != None and channel != None:
            self.mux_enabled = True
            self.mux = mux
            self.channel = channel
            self.channel_byte = self.get_channel_byte(self.channel)
        else:
            self.mux_enabled = False

        # Initialize i2c file reader and writer
        self.fr = io.open("/dev/i2c-" + str(bus), "rb", buffering=0)
        self.fw = io.open("/dev/i2c-" + str(bus), "wb", buffering=0)
        fcntl.ioctl(self.fr, self.I2C_SLAVE, self.address)
        fcntl.ioctl(self.fw, self.I2C_SLAVE, self.address)

        # Initialize logger names
        if self.mux_enabled:
            console_name = 'I2C({}.0x{:02X}.{}.0x{:02X})'.format(bus, mux, channel, address)
            file_name = 'i2c.{}.0x{:02X}.{}.0x{:02X}'.format(bus, mux, channel, address)
        else:
            console_name = 'I2C({}.0x{:02X})'.format(bus, address)
            file_name = 'i2c.{}.0x{:02X}'.format(bus, address)

        # Initialize logger instance
        extra = {'console_name':console_name, 'file_name': file_name}
        logger = logging.getLogger(__name__)
        self.logger = logging.LoggerAdapter(logger, extra)


    def write(self, byte_list, disable_mux=False):
        """ Writes byte list to device. Converts byte list to byte array then 
            sends bytes. """
        if not disable_mux:
            self.manage_mux()
        byte_array = bytearray(byte_list)
        byte_string = "".join('0x{:02X} '.format(b) for b in byte_array)
        self.logger.debug("Writing: {}".format(byte_string))


        self.fw.write(byte_array)


    def write_raw(self, bytes, disable_mux=False):
        """ Writes raw bytes to device. """
        if not disable_mux:
            self.manage_mux()
        self.logger.debug("Writing: {}".format(bytes))
        self.fw.write(bytes)


    def read(self, num_bytes, disable_mux=False):
        """ Reads num bytes from device. Returns byte array. """
        if not disable_mux:
            self.manage_mux()
        byte_array = bytearray(self.fr.read(num_bytes))
        byte_string = "".join('0x{:02X} '.format(b) for b in byte_array)
        self.logger.debug("Read: {}".format(byte_string))
        return byte_array


    def read_raw(self, num_bytes, disable_mux=False):
        """ Reads num bytes from device. Returns raw bytes. """
        if not disable_mux:
            self.manage_mux()
        bytes_ = self.fr.read(num_bytes)
        return bytes_


    def manage_mux(self):
        """ Sets mux to channel if enabled. """
        if self.mux_enabled:
            self.logger.debug("Setting mux 0x{:02X} to channel {}, writing: 0x{:02X}".format(self.mux, self.channel, self.channel_byte))
            byte_list = [self.channel_byte]
            byte_array = bytearray(byte_list)
            byte_string = "".join('0x{:02X} '.format(b) for b in byte_array)
            fcntl.ioctl(self.fw, self.I2C_SLAVE, self.mux)
            self.fw.write(byte_array)
            fcntl.ioctl(self.fw, self.I2C_SLAVE, self.address)


    def close(self):
        """ Closes device. """
        self.fw.close()
        self.fr.close()


################################# Helper Functions ############################


    def get_channel_byte(self, channel): 
        """ Converts channel int to channel byte. Verifies channel is
            between 0-7. """

        # Verify channel within valid range
        if (channel < 0) or (channel > 7):
            raise ValueError("Invalid channel value")

        # Calculate and return channel byte
        return 0x01 << channel