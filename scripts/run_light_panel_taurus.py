# Set system path to project root directory via relative imports
import sys
sys.path.append("../")

# Import standard python modules
import time, logging

# Import device comms
from device.comms.i2c import I2C

# Run main
if __name__ == "__main__":
    """ Runs light panel taurus for hardware testing. """

    # Initialize command line args
    no_mux = False
    set_mux = False
    logging_enabled = False
    on = False
    off = False
    fade_all = False
    fade_individual = False

    # Initialize fade parameters
    min_fade = 50
    max_fade = 210

    # Get device config from command line args
    if "--fs1" in sys.argv:
        print("Config: Food Server Rack v1 -- CONFIGURE ME")
        bus = None
        mux =None
        channel = None
        address = None
    elif "--edu1" in sys.argv:
        print("Config: PFC-EDU v1 -- CONFIGURE ME")
        bus = None
        mux =None
        channel = None
        address = None
    else:
        print("Config: Default")
        bus = 2
        mux =0x77
        channel = 1
        address = 0x47

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

    # Get output options from command line args
    if "--on" in sys.argv:
        on = True
    elif "--off" in sys.argv:
        off = True
    elif "--fade-all" in sys.argv:
        fade_all = True
    elif "--fade-indiv" in sys.argv:
        fade_individual = True
    else:
        print("No output option specified. \nPlease select one of the following:",
            "\n  --on", "\n  --off", "\n  --fade")
        sys.exit(0)

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

    # Set output
    if logging_enabled: print("Setting output")

    if on:
        print("Turning on")
        for ch in range(8):
            i2c.write([0x47, 0x30+ch, 0x00, 0x00])
    elif off:
        print("Turning off")
        for ch in range(8):
            i2c.write([0x47, 0x30+ch, 0x00, 0x00])
    elif fade_all:
        print("Fading all")
        # Fade up
        for val in range(min_fade, max_fade, 10):
            for ch in [0,2,4,5,6,7]:
                i2c.write([0x47, 0x30+ch, val, 0x00])
            time.sleep(0.001)
        # Fade down
        for val in range(max_fade, min_fade, -10):
            for ch in [0,2,4,5,6,7]:
                i2c.write([0x47, 0x30+ch, val, 0x00])
            time.sleep(0.001)
    elif fade_individual:
        print("Fading individual")
        for ch in [0,2,4,5,6,7]:
            # Fade up
            for val in range(min_fade, max_fade, 10):
                i2c.write([0x47, 0x30+ch, val, 0x00])
                time.sleep(0.001)
            # Fade down
            for val in range(max_fade, min_fade, -10):
                i2c.write([0x47, 0x30+ch, val, 0x00])
                time.sleep(0.001)


    # i2cset -y 2 0x4c $((0x30+$i)) 0x00 0x00 i


    