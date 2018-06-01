# Import standard python libraries
import sys, os, json, argparse, logging, time, shlex

# Import manager module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.modules.atlas_ec.manager import AtlasEC
except:
    # ... if running tests from same dir as manager.py
    sys.path.append("../../../../")
    from device.peripherals.modules.atlas_ec.manager import AtlasEC

# Import device utilities
from device.utilities.logger import Logger

# Import device state
from device.state import State

# Initialize state
state = State()

# Change directory for importing files
os.chdir("../../../../")

# Setup parser
parser = argparse.ArgumentParser(description="Test and debug AtlasEC hardware")
parser.add_argument("--debug", action="store_true", help="set logger in debug mode")
parser.add_argument("--info", action="store_true", help="set logger in info mode")
parser.add_argument("--loop", action="store_true", help="loop command prompt")

# Configs
parser.add_argument("--edu1", action="store_true", help="specify edu v1.0 config")

# Functions
parser.add_argument("--update", action="store_true", help="updates sensor")
parser.add_argument("--reset", action="store_true", help="resets sensor")
parser.add_argument("--shutdown", action="store_true", help="shuts down sensor")


if __name__ == "__main__":

    # Read in arguments
    args = parser.parse_args()

    # Initialize logger
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    elif args.info:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    # Initialize core
    if args.edu1:
        print("Configuring for pfc-edu v1.0")
        device_config = json.load(open("data/devices/edu1.json"))
        peripheral_config = device_config["peripherals"][1] # TODO make a function to pull out from name
        manager = AtlasEC("EDU1", state, peripheral_config)
        manager.initialize()
        manager.setup()
    else:
        print("Please specify a device configuraion")
        sys.exit(0)

    # Check for loop
    if args.loop:
        loop = True
    else:
        loop = False

    # Loop forever
    while True:

        # Check if updating
        if args.update:
            print("Updating")
            manager.update()

        # Check if resetting
        if args.reset:
            print("Resetting")
            manager.reset()

        # Check if updating
        if args.shutdown:
            print("Shutting down")
            manager.shutdown()

        # Check for new command if loop enabled
        if loop:
            new_command = input("New command: ")
            args = parser.parse_args(shlex.split(new_command))
        else:
            break
