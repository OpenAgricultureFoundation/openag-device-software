#!/usr/bin/env python3

# Import standard python modules
import os, time, sys

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

# https://www.ti.com/lit/ds/snas483f/snas483f.pdf
# http://e2e.ti.com/support/data-converters/f/73/t/508327#pi320995filter=all&pi320995scroll=false
# https://os.mbed.com/users/fblanc/code/ADC128D818/file/816284ff2a09/ADC128D818.cpp/
# http://eblot.github.io/pyftdi/api/i2c.html


# Legit addresses for ADC128D818
ADC_ADDRESS = [0x1D, 0x1E, 0x1F, 0x2D, 0x2E, 0x2F, 0x35, 0x36, 0x37]
ADC_ADDRESS = 0x4A  # should be at 0x1D, but I see 0x4A on the scan
# debugrob: above is wrong, should be 0x1D, maybe chip is not wired correctly?

# Limits
ADC_LIMIT_HIGH = 0x00
ADC_LIMIT_LOW = 0x01

# Registers
ADC_CONFIG = 0x00
ADC_INTERRUPT = 0x01
ADC_INTERRUPT_MASK = 0x03
ADC_CONV_RATE = 0x07
ADC_CH_DISABLE = 0x08
ADC_ONE_SHOT = 0x09
ADC_DEEP_SHUTDOWN = 0x0A
ADC_ADV_CONFIG = 0x0B
ADC_STATUS = 0x0C
ADC_CH_READ = 0x20
ADC_LIMIT_MIN = [0x2A, 0x2C, 0x2E, 0x30, 0x32, 0x34, 0x36, 0x38]
ADC_LIMIT_MAX = [0x2B, 0x2D, 0x2F, 0x31, 0x33, 0x35, 0x37, 0x39]
ADC_MANU_ID = 0x3E
ADC_REV_ID = 0x3F

# Channels
ADC_CHANNEL_IN0 = 0x00
ADC_CHANNEL_IN1 = 0x01
ADC_CHANNEL_IN2 = 0x02
ADC_CHANNEL_IN3 = 0x03
ADC_CHANNEL_IN4 = 0x04
ADC_CHANNEL_IN5 = 0x05
ADC_CHANNEL_IN6 = 0x06
ADC_CHANNEL_IN7 = 0x07
ADC_CHANNEL_TEMP = 0x07

ADC_ENABLE_IN0 = ~(0x01 << 0)
ADC_ENABLE_IN1 = ~(0x01 << 1)
ADC_ENABLE_IN2 = ~(0x01 << 2)
ADC_ENABLE_IN3 = ~(0x01 << 3)
ADC_ENABLE_IN4 = ~(0x01 << 4)
ADC_ENABLE_IN5 = ~(0x01 << 5)
ADC_ENABLE_IN6 = ~(0x01 << 6)
ADC_ENABLE_IN7 = ~(0x01 << 7)
ADC_ENABLE_TEMP = ~(0x01 << 7)
ADC_ENABLE_ALL = 0x00

ADC_INT_IN0 = ~(0x01 << 0)
ADC_INT_IN1 = ~(0x01 << 1)
ADC_INT_IN2 = ~(0x01 << 2)
ADC_INT_IN3 = ~(0x01 << 3)
ADC_INT_IN4 = ~(0x01 << 4)
ADC_INT_IN5 = ~(0x01 << 5)
ADC_INT_IN6 = ~(0x01 << 6)
ADC_INT_IN7 = ~(0x01 << 7)
ADC_INT_TEMP = ~(0x01 << 7)
ADC_INT_ALL = 0x00

# Status and config values
Busy_Status_Register_Not_Ready = 1 << 1
Advanced_Configuration_Register_External_Reference_Enable = 1 << 0
Advanced_Configuration_Register_Mode_Select_0 = 1 << 1
Advanced_Configuration_Register_Mode_Select_1 = 1 << 2
Configuration_Register_Start = 1 << 0
Configuration_Register_INT_Enable = 1 << 1
Configuration_Register_INT_Clear = 1 << 3
Configuration_Register_Initialization = 1 << 7


# Initialize i2c instance
i2c_controller = I2cController()
i2c_controller.configure("ftdi://ftdi:232h/1")
adc = i2c_controller.get_port(ADC_ADDRESS)

# Get the ADC status to see if it is ready
adc.write([ADC_STATUS])
bytes_ = adc.read(1)  # read one byte
# bytes_ = adc.read_from(ADC_STATUS, 1)
print("ADC_STATUS bytes={})".format(bytes_))
status = bytes_[0]
if (status & Busy_Status_Register_Not_Ready) == 1:
    print("ADC is busy, exiting.")
    sys.exit(0)
print("ADC is ready. (status={})".format(status))

# Default = 0000_0010 = 0x02
# bit 0 = 1: ADC128D818 is converting
# bit 1 = 1: Waiting for the power-up sequence to end (not ready)
# want 0x00 as status for OK.


# debugrob: get status correctly, before continuing
sys.exit(0)


# Read the IDs from the chip:
# Manufacturer's ID always defaults to 0000_0001 = 0x01
adc.write([ADC_MANU_ID])
manID_ = adc.read(2)
# manID_ = adc.read_from(ADC_MANU_ID, 1)
# debugrob: need to use read_from to read a register everywhere?

# Revision's ID always defaults to 0000_1001 = 0x09
adc.write([ADC_REV_ID])
revID_ = adc.read(2)
# revID_ = adc.read_from(ADC_REV_ID, 1)
print("ADC manufacturer ID={}, revision ID={})".format(manID_, revID_))


# Initialize the ADC ##########################################################

# Tell ADC to stop: config command + zero
adc.write_to(ADC_CONFIG, bytes(0x00))

# init the advance config register
cmd_data = 0x00
# ADC_VREF_INT use internal reference voltage
cmd_data &= ~Advanced_Configuration_Register_External_Reference_Enable
# ADC_MODE_0 see data sheet
cmd_data &= ~Advanced_Configuration_Register_Mode_Select_0
cmd_data &= ~Advanced_Configuration_Register_Mode_Select_1
print("debugrob ADC_ADV_CONFIG, cmd_data={}".format(cmd_data))
adc.write_to(ADC_ADV_CONFIG, bytes(cmd_data))

# init the conversion rate register, set to continous
cmd_data = 0x00
cmd_data |= Advanced_Configuration_Register_External_Reference_Enable
print("debugrob ADC_CONV_RATE, cmd_data={}".format(cmd_data))
adc.write_to(ADC_CONV_RATE, bytes(cmd_data))

# choose to enable or disable the channels using the Channel Disable Register
# debugrob cmd_data = ADC_ENABLE_TEMP & ADC_ENABLE_IN1
cmd_data = 0x00
print("debugrob ADC_CH_DISABLE, cmd_data={}".format(cmd_data))
adc.write_to(ADC_CH_DISABLE, bytes(cmd_data))

# using the Interrupt Mask Register
# debugrob: cmd_data = ADC_INT_TEMP
cmd_data = 0x00
print("debugrob ADC_INTERRUPT_MASK, cmd_data={}".format(cmd_data))
adc.write_to(ADC_INTERRUPT_MASK, bytes(cmd_data))

# set the high limit voltage for channel 0
high_limit_voltage = 0x80  # debugrob, WTF does this mean?
channel = 0
cmd = ADC_LIMIT_MIN[0] + (channel * 2) + ADC_LIMIT_HIGH
print("debugrob cmd={}".format(cmd))
adc.write_to(cmd, bytes(high_limit_voltage))

# Tell ADC to start: config command + start and interrupt enable
cmd_data = 0x00
cmd_data = Configuration_Register_Start | Configuration_Register_INT_Enable
print("debugrob ADC_CONFIG, cmd_data={}".format(cmd_data))
adc.write_to(ADC_CONFIG, bytes(cmd_data))

# Read channel input 0
channel = ADC_CHANNEL_IN0
cmd = ADC_CH_READ + channel
# debugrob: should this be a "write_to" for a register write??
adc.write([cmd])  # write the 'read channel zero' command
while True:
    bytes_ = adc.read(2)  # read two bytes for the value
    print("{} Channel 0={}".format(time.asctime(), bytes_))
    time.sleep(1)


# debugrob: later try to read temp?
