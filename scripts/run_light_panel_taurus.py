# Set system path to project root directory via relative imports
import sys
sys.path.append("../")

# Import standard python modules
import time, logging

# Import device comms
from device.comms.i2c import I2C

# Fade parameters
min_fade = 50
max_fade = 220
increment = 2
delay = 0.01
channels = [0,2,4,5,6,7]


# Device functions
def turn_on():
    """ Turns on light. """
    if logging_enabled: print("Turning on")

    # Turn all lights on
    for ch in channels:
        i2c.write([0x30+ch, 0x00, 0x00])


def turn_off():
    """ Turns off light. """
    if logging_enabled: print("Turning off")

    # Turn all lights off
    for ch in channels:
        i2c.write([0x30+ch, 0xff, 0x00])


def fade_all():
    """ Fades all light channels simultaneuosly. """
    if logging_enabled: print("Fading all")

    # Start with all lights off
    turn_off()

    # Fade lights forever!
    while True:
        # Fade up
        for val in range(max_fade, min_fade, -increment):
            for ch in [0,2,4,5,6,7]:
                i2c.write([0x30+ch, val, 0x00])
            time.sleep(delay)

        # Fade down
        for val in range(min_fade, max_fade, increment):
            for ch in [0,2,4,5,6,7]:
                i2c.write([0x30+ch, val, 0x00])
            time.sleep(delay)


def fade_individual():
    """ Fades individual light channels sequentially. """
    print("Fading individual")

    # Start with all lights off
    turn_off()

    # Fade lights forever!
    while True:
        for ch in channels:
            # Fade up
            for val in range(max_fade, min_fade, -increment):
                i2c.write([0x30+ch, val, 0x00])
                time.sleep(delay)
            
            # Fade down
            for val in range(min_fade, max_fade, increment):
                i2c.write([0x30+ch, val, 0x00])
                time.sleep(delay)


# Run main
if __name__ == "__main__":
    """ Runs light panel taurus for hardware testing. """

    # Initialize command line args
    no_mux = False
    set_mux = False
    logging_enabled = False
    set_on = False
    set_off = False
    set_fade_all = False
    set_fade_individual = False

    # Get device config from command line args
    if "--fs1" in sys.argv:
        print("Config: Food Server Rack v1 -- CONFIGURE ME")
        bus = None
        mux =None
        channel = None
        address = None
    elif "--edu1" in sys.argv:
        print("Config: PFC-EDU v1")
        bus = 2
        mux = 0x77
        channel = 3
        address = 0x47
    else:
        print("Please specify a device:\n  --fs1\n  --edu1")
        sys.exit(0)

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
        set_on = True
    elif "--off" in sys.argv:
        set_off = True
    elif "--fade-all" in sys.argv:
        set_fade_all = True
    elif "--fade-indiv" in sys.argv:
        set_fade_individual = True
    else:
        print("No output option specified. \nPlease select one of the following:",
            "\n  --on", "\n  --off", "\n  --fade-all", "\n  --fade-indiv")
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

    # Read power down register
    if logging_enabled: print("Reading power down register value")
    byte = i2c.read_register(0x40)
    print("Power Down Register Byte: 0x{:02X}".format(byte))

    # Set output
    if set_on:
        turn_on()
    elif set_off:
        turn_off()
    elif set_fade_all:
        fade_all()
    elif set_fade_individual:
        fade_individual()
