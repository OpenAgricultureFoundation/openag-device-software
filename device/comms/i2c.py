# Import standard python libraries
import fcntl, io, time, logging


class I2C(object):
    """ I2C communication device. Can communicate with device directly or 
        via an I2C mux. """

    # Initialize I2C communication options
    I2C_SLAVE=0x0703


    def __init__(self, bus, address, mux=None, channel=None):
        """ Initialize I2C device. """

        # Initialize standard i2c parameters
        self.bus = bus
        self.address = address

        # Initialize i2c mux parameters
        if mux != None and channel != None:
            self.mux = mux
            self.channel = channel
            self.mux_enabled = True
        else:
            self.mux_enabled = False

        # Initialize i2c file reader and writer
        self.fr = io.open("/dev/i2c-"+str(bus), "rb", buffering=0)
        self.fw = io.open("/dev/i2c-"+str(bus), "wb", buffering=0)
        fcntl.ioctl(self.fr, self.I2C_SLAVE, address)
        fcntl.ioctl(self.fw, self.I2C_SLAVE, address)

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


    def write(self, byte_list):
        """ Writes byte list to device. Converts byte list to byte array then 
            sends bytes. """
        byte_array = bytearray(byte_list)
        byte_string = "".join('0x{:02X} '.format(b) for b in byte_array)
        self.logger.debug("Writing: {}".format(byte_string))
        self.fw.write(byte_array)


    def write_raw(self, bytes):
        """ Writes raw bytes to device. """
        self.logger.debug("Writing: {}".format(bytes))
        self.fw.write(bytes)


    def read(self, num_bytes):
        """ Reads num bytes from device. Returns byte array. """
        byte_array = bytearray(self.fr.read(num_bytes))
        byte_string = "".join('0x{:02X} '.format(b) for b in byte_array)
        self.logger.debug("Read: {}".format(byte_string))
        return byte_array


    def read_raw(self, num_bytes):
        """ Reads num bytes from device. Returns raw bytes. """
        bytes = self.fr.read(num_bytes)
        return bytes


    def close(self):
        """ Closes device. """
        self.fw.close()
        self.fr.close()