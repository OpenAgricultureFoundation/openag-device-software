import time
from pyftdi.i2c import I2cController

# Initialize i2c instance
i2c_controller = I2cController()
i2c_controller.configure("ftdi://ftdi:232h/1")
i2c = i2c_controller.get_port(0x15)

# Get co2 data bytes
i2c.write([0x04, 0x13, 0x8a, 0x00, 0x01])  # status
bytes_ = i2c.read(4)

# Parse co2 data bytes
_, _, msb, lsb = bytes_
co2 = float(msb * 256 + lsb)
co2 = round(co2, 0)
print("CO2: {} ppm".format(co2))
