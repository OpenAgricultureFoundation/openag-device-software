import time
from pyftdi.i2c import I2cController

# Instanciate an I2C controller
i2c_controller = I2cController()

# Configure the first interface (IF/1) of the FTDI device as an I2C master
i2c_controller.configure("ftdi://ftdi:232h/1")

# Set mux
# i2c = i2c_controller.get_port(0x77)

# channel = 2
# channel_byte = 0x01 << channel

# # Write to the device
# i2c.write([channel_byte])

# Get temperature
# i2c = i2c_controller.get_port(0x40)

# # Write to the device
# i2c.write([0xf3])

# msb = i2c.read(1)

# print(msb)


# i2c.exchange([0xf3], 2)

# emit a START sequence is read address, but read no data and keep the bus
# busy
# i2c.read(0, relax=False)

# # wait for ~1ms
# time.sleep(0.001)

# # write 4 bytes, without neither emitting the start or stop sequence
# i2c.write(b"\xf3", relax=False, start=False)

# # read 4 bytes, without emitting the start sequence, and release the bus
# i2c.read(2, start=False)
