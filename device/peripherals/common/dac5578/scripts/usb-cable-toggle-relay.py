#!/usr/bin/env python3

# Import standard python modules
import os, time, sys

if len(sys.argv) == 1:  # no command line args
    print("Please provide the DAC channel (0 to 7) on the command line")
    exit(1)

# Import usb-to-i2c communication modules
from pyftdi.i2c import I2cController

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
i2c_controller = I2cController()
i2c_controller.configure("ftdi://ftdi:232h/1")
i2c = i2c_controller.get_port(0x47)

# Get the channel from the command line
channel = int(sys.argv[1])
byte = 0x30 + channel

# Toggle the channel high, wait a sec, then low.
i2c.write([byte, 0xFF, 0x00])  # to high
time.sleep(1)
i2c.write([byte, 0x00, 0x00])  # to low
