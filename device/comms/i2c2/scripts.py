# Import standard python libraries
import sys, os, json, argparse, logging, time, shlex

# Get current working directory
cwd = os.getcwd()
print("Running from: {}".format(cwd))

# Set correct import path
if cwd.endswith("i2c2"):
    print("Running locally")
    sys.path.append("../../../")
elif cwd.endswith("openag-device-software"):
    print("Running globally")
else:
    print("Running from invalid location")
    sys.exit(0)

# Import i2c comms
from device.comms.i2c2.main import I2C
from device.comms.i2c2.exceptions import InitError

# Enable logging output
logging.basicConfig(level=logging.DEBUG)


# def scan(address_range=None, mux_range=None, channel_range=None):
#     """Scan for devices at specified address, mux, and channel ranges."""
#     ...

if __name__ == "__main__":
    try:
        i2c = I2C("Test", 2, 0x40, 0x77, 2, None, None)
    except InitError:
        print("Unable to initialize I2C")
