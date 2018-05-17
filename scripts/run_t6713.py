# Set system path to project root directory via relative imports
import sys
sys.path.append("../")

# Import standard python modules
import time, logging

# Import device comms
from device.comms.i2c import I2C

# Run main
if __name__ == "__main__":
    """ Runs sht25 temperature and humidity sensor for hardware testing. """

    # Initialize command line args
    no_mux = False
    set_mux = False
    logging_enabled = False

    # Get device config from command line args
    if "--fs1" in sys.argv:
        print("Config: Food Server Rack v1")
        bus = 2
        mux =0x77
        channel = 2
        address = 0x15
    elif "--edu1" in sys.argv:
        print("Config: PFC-EDU v1")
        bus = 2
        mux =0x77
        channel = 2
        address = 0x15
    else:
        print("Config: Default")
        bus = 2
        mux =0x77
        channel = 2
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
        dev = I2C(bus=bus, address=mux)
    elif no_mux:
        # Initialize i2c communication directly with sensor
        dev = I2C(bus=bus, address=address)
    else:
        # Initialize i2c communication via mux with sensor
        dev = I2C(bus=bus, mux=mux, channel=channel, address=address)

    # Set mux then return if enabled
    if set_mux:
        # Set mux channel
        dev.write([channel])
        sys.exit()

    # Get co2
    if logging_enabled: print("Getting co2")
    dev.write([0x04, 0x13, 0x8b, 0x00, 0x01]) # Send read co2 command
    _, _, msb, lsb = dev.read(4, disable_mux=True)  # Read sensor data
    raw = float(msb*256 + lsb) # Convert co2 data
    co2 = float("{:.0f}".format(raw)) # Set significant figures
    print("CO2: {}".format(co2))

    # Get status
    if logging_enabled: print("Getting status")
    dev.write([0x04, 0x13, 0x8a, 0x00, 0x01]) # Send read status command
    _, _, status_msb, status_lsb = dev.read(4, disable_mux=True) # Read status data
    print("status_msb=0x{:02x}, status_lsb=0x{:02X}".format(status_msb, status_lsb))