#!/usr/bin/env python3

# https://www.nxp.com/docs/en/data-sheet/PCA9632.pdf
# https://os.mbed.com/users/nxp_ip/code/PCA9632_simple_operation_sample/file/8726e00b9c04/main.cpp/

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
#mux_address = int(os.getenv("DEFAULT_MUX_ADDRESS"), 16)
#i2c = i2c_controller.get_port(mux_address)
# Set MUX channel byte to 0, for the CNS v6
#channel = int(0)
#channel_byte = 0x01 << channel
# Write to the MUX, to set the channel number
#i2c.write([channel_byte])

# For the CNS v6 board
PCA9632_I2C_ADDRESS=0x62
R_BYTE=3
G_BYTE=4
B_BYTE=5

led = i2c_controller.get_port(PCA9632_I2C_ADDRESS)

# init
init = [0x80, 0x80, 0x21, 0x00, 0x00, 0x00, 0x40, 0x80, 0x02, 0xEA]
data = init
led.write(data)

print('red')
data[R_BYTE] = 0x0F # R
led.write(data)
time.sleep(1) 

print('green')
data[R_BYTE] = 0x00 # R off
data[G_BYTE] = 0x0F # G
led.write(data)
time.sleep(1) 

print('blue')
data[G_BYTE] = 0x00 # G off
data[B_BYTE] = 0x0F # B
led.write(data)
time.sleep(1) 

data[B_BYTE] = 0x00 # B off
led.write(data)
time.sleep(1) 


# blink some colors
print('blinking...')
for count in range(12):
    data[ 3 + ((count + 2) % 3) ] = 0xFF
    data[ 3 + ((count + 1) % 3) ] = 0x00
    data[ 3 + ((count + 0) % 3) ] = 0x00
    data[ 7 ] = 0
    data[ 8 ] = 0
    led.write(data)
    time.sleep(0.15) 

    data[ 3 ] = 0x00
    data[ 4 ] = 0x00
    data[ 5 ] = 0x00
    data[ 7 ] = 0
    data[ 8 ] = 0
    led.write(data)
    count += 1
    time.sleep(0.15) 

# some PWM fun
print('smooth PWM...')
for count in range(2048):
    data[ 3 + (((count >> 8) + 2) % 3) ] = 0xFF - (count & 0xFF)
    data[ 3 + (((count >> 8) + 1) % 3) ] = 0x00
    data[ 3 + (((count >> 8) + 0) % 3) ] = count & 0xFF
    data[ 7 ] = 0
    data[ 8 ] = 0
    led.write(data)
    count += 1
    time.sleep(0.0001) 

# turn off
data = [0x80, 0x80, 0x21, 0x00, 0x00, 0x00, 0x40, 0x80, 0x02, 0xEA]
led.write(data)

