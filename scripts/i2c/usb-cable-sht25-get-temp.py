#!/usr/bin/env python3

# Import standard python modules
import os, sys, time

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

# Get our I2C bus multiplexer (MUX).  
# It's really a DAC that lets us have 8 different I2C busses.
mux_address = int(os.getenv("DEFAULT_MUX_ADDRESS"), 16)
i2c = i2c_controller.get_port(mux_address)

# Set MUX channel byte to 2, for the PFC_EDU board and SHT25
channel = int(2)
channel_byte = 0x01 << channel

# Write to the MUX, to set the channel number
i2c.write([channel_byte])

# Set up to talk to the SHT25 at address 0x40
sht25 = i2c_controller.get_port(0x40)

# Write the wake up command to trigger a temperature measurement
sht25.write([0xE7])

# Wait for SHT25 to process
time.sleep(0.1) 

# Read one status byte.
status = sht25.read(1)

# Send read temp command
sht25.write([0xF3])
time.sleep(0.22) 

# Read two bytes, which is the temp in C
bytes_ = sht25.read(2)
msb, lsb = bytes_
raw = msb * 256 + lsb
temperature = float(-46.85 + ((raw * 175.72) / 65536.0))
tempC = float("{:.0f}".format(temperature))
print("{} C".format(tempC))


