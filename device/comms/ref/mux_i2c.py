# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
# Based on Adafruit_I2C.py created by Kevin Townsend.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import logging
import os, time
import subprocess
from device.comms.pysmbus import SMBus


class MuxI2C(object):
    """Class for communicating with an I2C device using the adafruit-pureio pure
    python smbus library, or other smbus compatible I2C interface. Allows reading
    and writing 8-bit, 16-bit, and byte array values to registers
    on the device."""
    def __init__(self, bus, mux, channel, address):
        """Create an instance of the I2C device at the specified address on the
        specified I2C bus number."""

        # Initialize i2c bus
        self._bus = SMBus(bus)

        # Initialize mux address and channel
        self._mux = mux
        self._channel = channel
        if channel > 0:
            self._channel_byte = 0x01 << (channel - 1) 
        else:
            self._channel_byte = 0x00

        # Initialize peripheral device address
        self._address = address

        # Initialize logger
        console_name = 'MuxI2C ({}.0x{:02X}.{}.0x{:02X})'.format(bus, mux, channel, address)
        file_name = 'muxi2c.{}.0x{:02X}.{}.0x{:02X}'.format(bus, mux, channel, address)
        extra = {'console_name':console_name, 'file_name': file_name}
        logger = logging.getLogger(__name__)
        self._logger = logging.LoggerAdapter(logger, extra)


        # Log initialization config
        self._logger.info("Initialized I2C comm on bus={}, mux=0x{:02X}, channel={}, address=0x{:02X}".format(bus, mux, channel, address))

    
    def setMux(self):
        """ Set mux to initialized channel. """
        self._logger.debug("Setting mux")
        self._bus.write_byte(self._mux, self._channel_byte)


    def writeRaw8(self, value):
        """Write an 8-bit value on the bus (without register)."""
        self.setMux()
        value = value & 0xFF
        self._bus.write_byte(self._address, value)
        self._logger.debug("Wrote 0x%02X", value)


    def write8(self, register, value):
        """Write an 8-bit value to the specified register."""
        self.setMux()
        value = value & 0xFF
        self._bus.write_byte_data(self._address, register, value)
        self._logger.debug("Wrote 0x%02X to register 0x%02X", value, register)


    def write16(self, register, value):
        """Write a 16-bit value to the specified register."""
        self.setMux()
        value = value & 0xFFFF
        self._bus.write_word_data(self._address, register, value)
        self._logger.debug("Wrote 0x%04X to register pair 0x%02X, 0x%02X",
                     value, register, register+1)


    def writeList(self, register, data):
        self.setMux()
        """Write bytes to the specified register."""
        self._bus.write_i2c_block_data(self._address, register, data)
        self._logger.debug("Wrote to register 0x%02X: %s",
                     register, data)


    def writeRawList(self, data):
        self.setMux()
        """ Writes raw list of data bytes. """
        for byte in data:
            self.writeRaw8(byte)


    def readRaw8(self):
        """Read an 8-bit value on the bus (without register)."""
        self.setMux()
        result = self._bus.read_byte(self._address) & 0xFF
        self._logger.debug("Read 0x%02X",
                    result)
        return result


    def readU8(self, register):
        """Read an unsigned byte from the specified register."""
        self.setMux()
        result = self._bus.read_byte_data(self._address, register) & 0xFF
        self._logger.debug("Read 0x%02X from register 0x%02X",
                     result, register)
        return result


    def readS8(self, register):
        """Read a signed byte from the specified register."""
        self.setMux()
        result = self.readU8(register)
        if result > 127:
            result -= 256
        return result


    def readU16(self, register, little_endian=True):
        """Read an unsigned 16-bit value from the specified register, with the
        specified endianness (default little endian, or least significant byte
        first)."""
        self.setMux()
        result = self._bus.read_word_data(self._address,register) & 0xFFFF
        self._logger.debug("Read 0x%04X from register pair 0x%02X, 0x%02X",
                           result, register, register+1)
        # Swap bytes if using big endian because read_word_data assumes little
        # endian on ARM (little endian) systems.
        if not little_endian:
            result = ((result << 8) & 0xFF00) + (result >> 8)
        return result


    def readS16(self, register, little_endian=True):
        """Read a signed 16-bit value from the specified register, with the
        specified endianness (default little endian, or least significant byte
        first)."""
        self.setMux()
        result = self.readU16(register, little_endian)
        if result > 32767:
            result -= 65536
        return result


    def readU16LE(self, register):
        """Read an unsigned 16-bit value from the specified register, in little
        endian byte order."""
        self.setMux()
        return self.readU16(register, little_endian=True)


    def readU16BE(self, register):
        """Read an unsigned 16-bit value from the specified register, in big
        endian byte order."""
        self.setMux()
        return self.readU16(register, little_endian=False)


    def readS16LE(self, register):
        """Read a signed 16-bit value from the specified register, in little
        endian byte order."""
        self.setMux()
        return self.readS16(register, little_endian=True)


    def readS16BE(self, register):
        """Read a signed 16-bit value from the specified register, in big
        endian byte order."""
        self.setMux()
        return self.readS16(register, little_endian=False)


    def readList(self, register, length):
        """Read a length number of bytes from the specified register.  Results
        will be returned as a bytearray."""
        self.setMux()
        results = self._bus.read_i2c_block_data(self._address, register, length)
        self._logger.debug("Read the following from register 0x%02X: %s",
                     register, results)
        return results


    def readRawList(self, length):
        self.setMux()
        """ Reads a length number of raw bytes. Results will be returned as 
            a bytearray. """
        result = self._bus.read_bytes(self._address, length)
        self._logger.info(result)
        return result

