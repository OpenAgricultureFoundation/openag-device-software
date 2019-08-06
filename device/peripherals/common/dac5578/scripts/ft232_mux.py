#!/usr/bin/env python3

# Import standard python modules
import os, sys

if len( sys.argv ) == 1: # no command line args
    print("Please provide the multiplexer channel (0 to 7) on the command line")
    exit(1)

# Import usb-to-i2c communication modules
from pyftdi.ftdi import Ftdi
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
mux_address = int(os.getenv("DEFAULT_MUX_ADDRESS"), 16)
i2c = i2c_controller.get_port(mux_address)

# Get channel byte
channel = int(sys.argv[1])
channel_byte = 0x01 << channel

# Write to the device
i2c.write([channel_byte])
