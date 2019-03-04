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
ADC_ADDRESS         = [0x1d, 0x1e, 0x1f, 0x2d, 0x2e, 0x2f, 0x35, 0x36, 0x37]
ADC_ADDRESS         = 0x4A # should be at 0x35, but I see 4A on the scan

# Support Values
READ = 0
WRITE = 1

# Register
ADC_CONFIG          = 0x00
ADC_INTERRUPT       = 0x01
ADC_INTERRUPT_MASK  = 0x03
ADC_CONV_RATE       = 0x07
ADC_CH_DISABLE      = 0x08
ADC_ONE_SHOT        = 0x09
ADC_DEEP_SHUTDOWN   = 0x0a
ADC_ADV_CONFIG      = 0x0b
ADC_STATUS          = 0x0c
ADC_CH_READ         = 0x20 
ADC_LIMIT_MIN       = [0x2a, 0x2c, 0x2e, 0x30, 0x32, 0x34, 0x36, 0x38]
ADC_LIMIT_MAX       = [0x2b, 0x2d, 0x2f, 0x31, 0x33, 0x35, 0x37, 0x39]
ADC_MANU_ID         = 0x3e
ADC_REV_ID          = 0x3f

# Channels
ADC_CHANNEL_IN0     = 0x00
ADC_CHANNEL_IN1     = 0x01
ADC_CHANNEL_IN2     = 0x02
ADC_CHANNEL_IN3     = 0x03
ADC_CHANNEL_IN4     = 0x04
ADC_CHANNEL_IN5     = 0x05
ADC_CHANNEL_IN6     = 0x06
ADC_CHANNEL_IN7     = 0x07
ADC_CHANNEL_TEMP    = 0x07

Busy_Status_Register_Not_Ready = 1<<1


# Initialize i2c instance
i2c_controller = I2cController()
i2c_controller.configure("ftdi://ftdi:232h/1")
adc = i2c_controller.get_port(ADC_ADDRESS)

#print("Status={}".format( adc.read(ADC_STATUS)))

cmd = ADC_STATUS
adc.write([cmd])
bytes_ = adc.read(1) # read one byte
status = bytes_[0]
if (status & Busy_Status_Register_Not_Ready) == 1:
    print("ADC is busy, exiting.")
    sys.exit(0)
print("ADC is ready. (status={})".format(status))


# write config mode 0
#adc.write_to(ADC_CONFIG, 0x00)

# write one byte to read a channel, then receive two bytes
#cmd = ADC_CH_READ + ADC_CHANNEL_IN0 # read channel 0
#bytes_ = adc.exchange([cmd], 2)
#print("Channel 0={}".format( bytes_))

#bytes_ = adc.read(ADC_CHANNEL_IN0, 2)
#bytes_ = adc.read(ADC_CH_READ, 2)
#print("Channel 0={}".format( bytes_))

#bytes_ = adc.read(ADC_CHANNEL_TEMP, readlen=2)
#print("Temp={}".format( adc.read(ADC_CHANNEL_TEMP)))






