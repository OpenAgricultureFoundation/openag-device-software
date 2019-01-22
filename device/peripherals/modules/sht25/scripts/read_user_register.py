# Import standard python modules
import os, time

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
i2c = i2c_controller.get_port(0x40)

# Read user register
byte_raw = i2c.read_from(0xE7, readlen=1)
byte = int(byte_raw[0])
print(byte)
print(type(byte))

# # Wait for sensor to process
# time.sleep(0.1)

# # Get raw bytes
# msb, lsb, checksum = i2c.read(3)

# # Compute temperature
# raw = msb * 256 + lsb
# temperature = float(-46.85 + ((raw * 175.72) / 65536.0))
# temperature = float("{:.0f}".format(temperature))

# # Display temperature
# print("Temperature: {} C".format(temperature))
