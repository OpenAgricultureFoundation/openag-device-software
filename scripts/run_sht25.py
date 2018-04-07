# Set system path to project root directory via relative imports
import sys
sys.path.append("../")

# Import standard python modules
import time, logging

# Import device comms
from device.comms.i2c import I2C
from device.comms.mux_i2c import MuxI2C

# Run main
if __name__ == "__main__":
    """ Runs isolated sht25 temperature and humidity sensor for hardware
        testing purposes. """

    # Initialize command line args
    no_mux = False
    set_mux = False
    logging_ = False

    # Get device config from command line args
    if "--fs1" in sys.argv:
        print("Config: Food Server Rack v1")
        bus = 2
        mux =0x77
        channel = 1
        address = 0x40
    elif "--edu1" in sys.argv:
        print("Config: PFC-EDU v1")
        bus = 2
        mux =0x77
        channel = 1
        address = 0x40
    else:
        print("Config: Default")
        bus = 2
        mux =0x77
        channel = 1
        address = 0x40

    # Get run options from command line args
    if '--no-mux' in sys.argv:
        print("Running with no mux!")
        no_mux = True
    if "--set-mux" in sys.argv:
        print("Setting mux!")
        set_mux = True
    if "--logging" in sys.argv:
        logging_ = True
        print("Logging enabled!")

    # Initialize logging if enabled
    if logging_:
        logging.basicConfig(level=logging.DEBUG)

    # Initialize i2c communication
    if set_mux:
        # Initialize i2c communication directly with mux
        i2c = I2C(bus=bus, address=mux)
    elif no_mux:
        # Initialize i2c communication directly with sht25
        i2c = I2C(bus=bus, address=address)
    else:
        # Initialize i2c communication via mux for sht25
        i2c = MuxI2C(bus=bus, mux=mux, channel=channel, address=address)

    # Set mux then return if enabled
    if set_mux:
        # Set mux channel
        i2c.writeRaw8(channel)
        sys.exit()

    # Get temperature
    i2c.writeRaw8(0xF3) # Send get temperature command (no hold master)
    time.sleep(0.5) # Wait for sensor to process
    data0 = i2c.readRaw8() # Read sensor data
    data1 = i2c.readRaw8()
    temperature = data0 * 256 + data1  # Convert temperature data
    temperature = -46.85 + ((temperature * 175.72) / 65536.0)
    temperature = float("%.1f"%(temperature)) # Set significant figures
    print("Temperature: {}".format(temperature))

    # Get humidity
    i2c.writeRaw8(0xF5) # Send get humidity command (no hold master)
    time.sleep(0.5) # Wait for sensor to process
    data0 = i2c.readRaw8() # Read sensor data
    data1 = i2c.readRaw8()
    humidity = data0 * 256 + data1 # Convert humidity data
    humidity = -6 + ((humidity * 125.0) / 65536.0)
    humidity = float("%.1f"%(humidity)) # Set significant figures
    print("Humidity: {}".format(humidity))