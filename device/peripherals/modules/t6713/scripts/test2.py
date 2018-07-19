import sys, os, json, argparse, logging, time, shlex

sys.path.append("../../../../../")

from device.comms.i2c2.main import I2C

i2c = I2C(name="Test", bus=2, address=0x15, mux=0x77, channel=0)

i2c.write(bytes([0x04, 0x13, 0x8b, 0x00, 0x01]))  # Co2
bytes_ = i2c.read(4, disable_mux=True)

print(bytes_)
