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

# For the CNS v6 board
PCA9632_I2C_ADDRESS = 0x62
R_BYTE = 3
G_BYTE = 4
B_BYTE = 5

led = i2c_controller.get_port(PCA9632_I2C_ADDRESS)

# Initialize led state
init = [0x80, 0x80, 0x21, 0x00, 0x00, 0x00, 0x40, 0x80, 0x02, 0xEA]
data = init
led.write(data)

# Set only green on
data[R_BYTE] = 0x00  # R off
data[G_BYTE] = 0x00  # G off
data[B_BYTE] = 0x00  # B off

led.write(data)
time.sleep(1)
