# Set system path to project root directory via relative imports
import sys
sys.path.append("../")

# Import standard python modules
import time, logging

# Import device comms
from device.comms.i2c import I2C

# Run main
if __name__ == "__main__":
    """ Runs t6713 co2 sensor for hardware testing. """

    # Initialize command line args
    no_mux = False
    set_mux = False
    logging_enabled = False

    # Get device config from command line args
    if "--fs1" in sys.argv:
        print("Config: Food Server Rack v1")
        bus = 2
        mux =0x77
        channel = 1
        address = 0x15
    elif "--edu1" in sys.argv:
        print("Config: PFC-EDU v1")
        bus = 2
        mux =0x77
        channel = 1
        address = 0x15
    else:
        print("Config: Default")
        bus = 2
        mux =0x77
        channel = 1
        address = 0x15

    # Get run options from command line args
    if '--no-mux' in sys.argv:
        print("Running with no mux!")
        no_mux = True
    if "--set-mux" in sys.argv:
        print("Setting mux!")
        set_mux = True
    if "--logging" in sys.argv:
        logging_enabled = True
        print("Logging enabled!")

    # Activate logging if enabled
    if logging_enabled:
        logging.basicConfig(level=logging.DEBUG)

    # Initialize i2c communication
    if set_mux:
        # Initialize i2c communication directly with mux
        i2c = I2C(bus=bus, address=mux)
    elif no_mux:
        # Initialize i2c communication directly with sensor
        i2c = I2C(bus=bus, address=address)
    else:
        # Initialize i2c communication via mux with sensor
        i2c = I2C(bus=bus, mux=mux, channel=channel, address=address)

    # Set mux then return if enabled
    if set_mux:
        # Set mux channel
        i2c.write([channel])
        sys.exit()

    # Get status
    if logging_enabled: print("Getting status")
    i2c.write([0x04, 0x13, 0x8a, 0x00, 0x01]) # Send get status command
    time.sleep(0.1) # Wait for sensor to process
    xx, xx, msb, lsb = i2c.read(4) # Read sensor data
    status = msb*256 + lsb # Convert sensor data
    print("Status: 0x{:04X}".format(status))

    # Get co2
    if logging_enabled: print("Getting co2")
    i2c.write([0x04, 0x13, 0x8b, 0x00, 0x01])
    time.sleep(0.1) # Wait for sensor to process
    xx, xx, msb, lsb = i2c.read(4) # Read sensor data
    co2 = msb*256 + lsb # Convert sensor data
    co2 = int(co2) # Set significant figures
    print("Co2: {}".format(co2))