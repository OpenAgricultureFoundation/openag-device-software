# Set system path to project root directory via relative imports
import sys
sys.path.append("../")

# Import standard python modules
import time, logging

# Import device comms
from device.comms.i2c import I2C


class LightArrayTaurus:
    """ An array of taurus light panels. """

    # Fade parameters
    min_fade = 50
    max_fade = 220
    increment = 3
    delay = 0.01
    channels = [0,2,4,5,6,7]


    def __init__(self, devices):
        """ Initializes light array taurus. """
        self.devices = devices

        # Initialize i2c communication
        for device in self.devices:
            device["i2c"] = I2C(bus=device["bus"], mux=device["mux"], channel=device["channel"], address=device["address"])


    def turn_on(self):
        """ Turns on light. """
        for device in self.devices:
            if logging_enabled: print("Turning on panel x,y: {},{}".format(device["x"], device["y"]))

            # Turn all lights on
            try:
                for ch in self.channels:
                    device["i2c"].write([0x30+ch, 0x00, 0x00])
                print("Turned on panel x,y: {},{}".format(device["x"], device["y"]))
            except Exception as e:
                print("Unable to turn on panel x,y: {},{}. {}".format(device["x"], device["y"], e))


    def turn_off(self):
        """ Turns off light. """
        for device in self.devices:
            if logging_enabled: print("Turning off panel x,y: {},{}".format(device["x"], device["y"]))

            # Turn all lights off
            try:
                for ch in self.channels:
                    device["i2c"].write([0x30+ch, 0xff, 0x00])
                print("Turned off panel x,y: {},{}".format(device["x"], device["y"]))
            except Exception as e:
                print("Unable to turn off panel x,y: {},{}. {}".format(device["x"], device["y"], e))


    def fade_all(self):
        """ Fades all light channels simultaneusosly. """
        if logging_enabled: print("Fading all")

        # Start with all lights off
        self.turn_off()

        # Fade lights forever!
        while True:
            # Fade up
            for val in range(self.max_fade, self.min_fade, -self.increment):
                for device in self.devices:
                    for ch in self.channels:
                        device["i2c"].write([0x30+ch, val, 0x00])
                time.sleep(self.delay)

            # Fade down
            for val in range(self.min_fade, self.max_fade, self.increment):
                for device in self.devices:
                    for ch in self.channels:
                        device["i2c"].write([0x30+ch, val, 0x00])
                time.sleep(self.delay)


    def fade_individual(self):
        """ Fades all panels' individual light channels sequentially. """
        print("Fading individual")

        # Start with all lights off
        self.turn_off()

        # Fade lights forever!
        while True:
            for ch in self.channels:
                # Fade up
                for val in range(self.max_fade, self.min_fade, -self.increment):
                    for device in self.devices:
                        device["i2c"].write([0x30+ch, val, 0x00])
                    time.sleep(self.delay)
                
                # Fade down
                for val in range(self.min_fade, self.max_fade, self.increment):
                    for device in self.devices:
                        device["i2c"].write([0x30+ch, val, 0x00])
                    time.sleep(self.delay)


    def fade_individual_sequential(self):
        """ Fades individual light channels sequentially running through panels sequentially. """
        print("Fading individual sequentially")

        # Start with all lights off
        self.turn_off()

        # Fade lights forever!
        while True:
            for device in self.devices:
                for ch in self.channels:
                    # Fade up
                    for val in range(self.max_fade, self.min_fade, -self.increment):
                        device["i2c"].write([0x30+ch, val, 0x00])
                        time.sleep(self.delay)
                    
                    # Fade down
                    for val in range(self.min_fade, self.max_fade, self.increment):
                        device["i2c"].write([0x30+ch, val, 0x00])
                        time.sleep(self.delay)


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
    set_fade_individual_sequential = False

    # Get device config from command line args
    if "--smhz1" in sys.argv:
        print("Config: Small Hazel v1")
        devices = [
            {"bus": 2, "mux": 0x77, "channel": 2, "address": 0x47, "x": 0, "y": 0},
            {"bus": 2, "mux": 0x77, "channel": 3, "address": 0x47, "x": 1, "y": 0}
        ]
    else:
        print("Please specify configuration:\n  --smhz1")

    # Get run options from command line args
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
    elif "--fade-indiv-seq" in sys.argv:
        set_fade_individual_sequential = True
    else:
        print("No output option specified. \nPlease select one of the following:"
            "\n  --on\n  --off\n  --fade-all\n  --fade-indiv\n  --fade-indiv-seq")
        sys.exit(0)

    # Activate logging if enabled
    if logging_enabled:
        logging.basicConfig(level=logging.DEBUG)

    # Instantiate light array taurus
    light_array_taurus = LightArrayTaurus(devices)

    # Set output
    if set_on:
        light_array_taurus.turn_on()
    elif set_off:
        light_array_taurus.turn_off()
    elif set_fade_all:
        light_array_taurus.fade_all()
    elif set_fade_individual:
        light_array_taurus.fade_individual()
    elif set_fade_individual_sequential:
        light_array_taurus.fade_individual_sequential()



