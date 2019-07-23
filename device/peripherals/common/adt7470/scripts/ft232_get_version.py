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

# Initialize constants
I2C_ADDRESS = 0x2E

# Initialize registers
VERSION_REGISTER = 0x3F
CONFIG_REGISTER_1 = 0x40
CONFIG_REGISTER_2 = 0x74
TEMPERATURE_BASE_REGISTER = 0x20
MAX_TEMPERATURE_REGISTER = 0x78
TEMPERATURE_LIMIT_BASE_REGISTER = 0x44

# Initialize masks
START_MONITORING_MASK = 0x80
STOP_MONITORING_MASK = 0x7F
POWER_DOWN_MASK = 0x01

# Initialize i2c
i2c_controller = I2cController()
i2c_controller.configure("ftdi://ftdi:232h/1")
i2c = i2c_controller.get_port(I2C_ADDRESS)


# Get version
print("Getting version...")
register_byte = bytes(i2c.read_from(VERSION_REGISTER, 1))
print("Version: {}".format(register_byte))
