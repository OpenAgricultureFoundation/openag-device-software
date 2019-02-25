#!/usr/bin/env python3

# Import standard python modules
import os, logging

# Import usb-to-i2c communication modules
from pyftdi.i2c import I2cController, I2cNackError

# Ensure virtual environment is activated
if os.getenv("VIRTUAL_ENV") == None:
    print("Please activate your virtual environment then re-run script")
    exit(0)

# Ensure platform info is sourced
if os.getenv("PLATFORM") == None:
    print("Please source your platform info then re-run script")
    exit(0)

# Ensure platform is usb-to-i2c enabled
if os.getenv("IS_USB_I2C_ENABLED") != "true":
    print("Platform is not usb-to-i2c enabled")
    exit(0)

# Initialize i2c instance
url = os.environ.get("FTDI_DEVICE", "ftdi://ftdi:232h/1")
i2c = I2cController()
slaves = []
logging.getLogger("pyftdi.i2c").setLevel(logging.ERROR)

# Scan for i2c devices
try:
    i2c.set_retry_count(1)
    i2c.configure(url)
    for addr in range(i2c.HIGHEST_I2C_ADDRESS + 1):
        port = i2c.get_port(addr)
        try:
            port.read(0)
            slaves.append("X")
        except I2cNackError:
            slaves.append(".")
finally:
    i2c.terminate()

# Initialize display variables
columns = 16
row = 0

# Display results
print("   %s" % "".join(" %01X " % col for col in range(columns)))
while True:
    chunk = slaves[row:row + columns]
    if not chunk:
        break
    print(" %1X:" % (row // columns), "  ".join(chunk))
    row += columns
