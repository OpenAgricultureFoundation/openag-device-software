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

# Initialize i2c instance with the USB-I2C cable
i2c_controller = I2cController()
i2c_controller.configure("ftdi://ftdi:232h/1")

# Get our I2C bus multiplexer (MUX).  
# It's really a DAC that lets us have 8 different I2C busses.
mux_address = int(os.getenv("DEFAULT_MUX_ADDRESS"), 16)
i2c = i2c_controller.get_port(mux_address)

# Set MUX channel byte to 3, for the PFC_EDU board and 6 color LED DAC.
channel = int(3)
channel_byte = 0x01 << channel

# Write to the MUX, to set the channel number
i2c.write([channel_byte])

# Set up to talk to the LED DAC at I2C address 0x47
led_dac = i2c_controller.get_port(0x47)

# Write the color channel and intensity
chan = 0 # far red
on = 0xFF # full intensity
off = 0x00 # off
chanadx = 0x30 + chan
led_dac.write([chanadx, on, 0x00, chan])

time.sleep(2)
led_dac.write([chanadx, off, 0x00, chan])


