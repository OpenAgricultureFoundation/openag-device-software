#!/usr/bin/env python3

# A convient script to program the I2C atlas chips we use.  
# This is the data sheet for the water temp sensor:
# https://www.atlas-scientific.com/_files/_datasheets/_circuit/EZO_RTD_Datasheet.pdf

# Hook up the atlas chip on a breadboard and wire up a USB-I2C cable to a PC.
# - GND is the left top pin on the chip (diamond end).  Wire to cable.
# - TX / SDA is the center top pin on the chip (diamond end).
# - RX / SCL is the right top pin on the chip (diamond end).
# - VCC is the lower left pin, wire to the 3.3V of the USB-I2C cable.

# Import standard python modules
import os, sys, time

if len( sys.argv ) <= 2: # missing command line args
    print("Please provide the CURRENT atlas chip I2C address on the command line in DECIMAL, FOLLOWED by the NEW I2C address you want set.")
    print("Example:  102 103")
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

current_i2c_address = int(sys.argv[1])
print("Current I2C address {}".format(current_i2c_address))

new_i2c_address = sys.argv[2]
print("New I2C address {}".format(new_i2c_address))

# Get the device at that address
slave = i2c_controller.get_port(current_i2c_address)

# I2C command to write
change_I2C_adx = bytes("I2C," + new_i2c_address, 'utf-8')
cmd = change_I2C_adx

# Write to the device
print("Sending {}".format(cmd))
slave.write(cmd)

#time.sleep(0.4)
#print("Read {}".format(slave.read()))
