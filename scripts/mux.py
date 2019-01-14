from pyftdi.ftdi import Ftdi

from pyftdi.i2c import I2cController

# Instanciate an I2C controller
i2c_controller = I2cController()

# Configure the first interface (IF/1) of the FTDI device as an I2C master
i2c_controller.configure("ftdi://ftdi:232h/1")

# Get a port to an I2C slave device
i2c = i2c_controller.get_port(0x77)

channel = 2
channel_byte = 0x01 << channel

# Write to the device
i2c.write([channel_byte])
