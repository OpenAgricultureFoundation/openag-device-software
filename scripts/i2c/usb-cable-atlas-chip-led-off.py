#!/usr/bin/env python3

# A convient script to program the I2C atlas chips we use.  
# This is the data sheet for the water temp sensor:
# https://www.atlas-scientific.com/_files/_datasheets/_circuit/EZO_RTD_Datasheet.pdf

# Import standard python modules
import os, sys, time

if len( sys.argv ) == 1: # no command line args
    print("Please provide the atlas chip I2C address on the command line in DECIMAL. e.g. 102")
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
i2c_address = int(sys.argv[1])
print("Using I2C address {}".format(i2c_address))

# Get the device at that address
slave = i2c_controller.get_port(i2c_address)

# I2C command to write
LED_off = b"L,0"
cmd = LED_off

# Write to the device
print("Sending {}".format(cmd))
slave.write(cmd)

