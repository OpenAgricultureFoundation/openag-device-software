import sys, os, json, argparse, logging, time, shlex

sys.path.append("../../../../../")

from device.comms.i2c import I2C

i2c = I2C(name="Test", bus=2, address=0x15, simulate=False)

i2c.write([0x04, 0x13, 0x8b, 0x00, 0x01], disable_mux=False)  # Co2
bytes_, error = i2c.read(4)

print(bytes_)
