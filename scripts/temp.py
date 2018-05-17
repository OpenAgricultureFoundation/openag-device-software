# Set system path to project root directory via relative imports
import sys
sys.path.append("../")

import time

# Import device comms
# from device.comms.ref.pysmbus import SMBus

# device = SMBus(bus=2)
# b = device.read_byte_data(0x40, 0xE7)
# print(b)

import logging
logging.basicConfig(level=logging.DEBUG)

from device.comms.i2c import I2C

# dev = I2C(bus=2, address=0x40)
dev = I2C(bus=2, mux=0x77, channel=2, address=0x40)

dev.write([0xE7])
time.sleep(0.5)
b = dev.read(1)

print("0x{:02X}, {}".format(b[0], type(b[0])))


