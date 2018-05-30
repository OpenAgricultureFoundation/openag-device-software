# Import standard python libraries
import sys, argparse, logging, time, shlex

# Import driver module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.drivers.dac5578.manager import DAC5578Manager
except:
    # ... if running tests from same dir as dac5578.py
    sys.path.append("../../../")
    from device.drivers.dac5578.manager import DAC5578Manager


# Import device utilities
from device.utilities.logger import Logger

# Setup parser
parser = argparse.ArgumentParser(description="Test and debug DAC5578 hardware")
parser.add_argument("--edu1", action="store_true", help="specifies edu config")
parser.add_argument("--debug", action="store_true", help="sets logger in debug mode")
parser.add_argument("--info", action="store_true", help="sets logger in info mode")
parser.add_argument("--probe", action="store_true", help="probes DAC")
parser.add_argument("-c", "--channel", type=int, help="specifies channel (0-7)")
parser.add_argument("-v", "--value", type=int, help="specifies output value (0-100)")
parser.add_argument("--on", action="store_true", help="turns on LEDs, can specify channel")
parser.add_argument("--off", action="store_true", help="turns off LEDs, can specify channel")
parser.add_argument("--fade", action="store_true", help="fades LEDs, can specify channel")
parser.add_argument("--reset", action="store_true", help="resets DAC5578")
parser.add_argument("--shutdown", action="store_true", help="shutsdown DAC5578")


if __name__ == "__main__":

    # Read in arguments
    args = parser.parse_args()

    # Check for logger
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    elif args.info:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    # Initialize core
    if args.edu1:
        print("Configuring for pfc-edu v1.0")
        dac5578_manager = DAC5578Manager("Test", 2, 0x47, mux=0x77, channel=3)
    else:
        print("Please specify a device configuraion")
        sys.exit(0)


    first = True
    while True:

        # Check if new command
        if not first:
            args = parser.parse_args(shlex.split(new_command))
        first = False

        # Check if resetting
        if args.reset:
            print("Resetting")
            dac5578_manager.reset()
            print("Reset successful")

        # Check if shutting down
        elif args.shutdown:
            print("Shutting down")
            dac5578_manager.shutdown()
            print("Shutdown successful")

        # Check if probing
        elif args.probe:
            print("Probing")
            error = dac5578_manager.probe()
            if error.exists():
                print("error = {}".format(error.trace))
            else:
                print("Probe successful")

        # Check if turning device on
        elif args.on:
            print("Turning on {channel}".format(channel = "all channels" if \
                args.channel == None else "channel: " + str(args.channel)))
            error = dac5578_manager.turn_on(channel=args.channel)
            if error.exists():
                print("Error: {}".format(error.trace))

        # Check if turning device off
        elif args.off:
            print("Turning off {channel}".format(channel = "all channels" if \
                args.channel == None else "channel: " + str(args.channel)))
            error = dac5578_manager.turn_off(channel=args.channel)
            if error.exists():
                print("Error: {}".format(error.trace))

        # Check if fading
        elif args.fade:
            print("Fading {channel}".format(channel = "all channels" if args.channel == None else "channel: " + str(args.channel)))
            error = dac5578_manager.fade(cycles=10, channel=args.channel)
            if error.exists():
                print("Error: {}".format(error.trace))

        # Check if setting a channel to a value
        elif args.channel != None and args.value != None:
            print("Setting channel {} to {}%".format(args.channel, args.value))
            error = dac5578_manager.set_output(args.channel, args.value)
            if error.exists():
                print("Error: {}".format(error.trace))

        # Check for new command
        new_command = input("New command: ")