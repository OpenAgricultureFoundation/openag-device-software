# Import standard python modules
import os

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

# Initialize i2c instance
i2c_controller = I2cController()
i2c_controller.configure("ftdi://ftdi:232h/1")
i2c = i2c_controller.get_port(0x15)

# Get co2 data bytes
i2c.write([0x04, 0x13, 0x8A, 0x00, 0x01])  # status
bytes_ = i2c.read(4)

# Parse co2 data bytes
_, _, msb, lsb = bytes_
co2 = float(msb * 256 + lsb)
co2 = round(co2, 0)
print("CO2: {} ppm".format(co2))
