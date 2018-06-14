# Import standard python libraries
import sys, os, json, argparse, logging, time, shlex

# Import manager module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.modules.atlas_ec.manager import AtlasECManager
except:
    # ... if running tests from same dir as manager.py
    os.chdir("../../../../")
    from device.peripherals.modules.atlas_ec.manager import AtlasECManager

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.accessors import get_peripheral_config

# Import device state
from device.state import State

# Initialize state
state = State()

# Setup parser basics
parser = argparse.ArgumentParser(description="Test and debug AtlasEC hardware")
parser.add_argument("--debug", action="store_true", help="set logger in debug mode")
parser.add_argument("--info", action="store_true", help="set logger in info mode")
parser.add_argument("--loop", action="store_true", help="loop command prompt")

# Setup parser configs
parser.add_argument("--device", type=str, help="specifies device config")

# Setup parser functions
parser.add_argument("--update", action="store_true", help="updates sensor")
parser.add_argument("--reset", action="store_true", help="resets sensor")
parser.add_argument("--shutdown", action="store_true", help="shuts down sensor")

# Run main
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

    # Check for device config
    if args.device != None:
        print("Using device config: {}".format(args.device))
        device_config = json.load(open("data/devices/{}.json".format(args.device)))
        peripheral_config = get_peripheral_config(device_config["peripherals"], "AtlasEC-Reservoir")
    else:
        print("Please specify a device configuraion")
        sys.exit(0)

    # Initialize manager
    manager = AtlasECManager(
        name = "AtlasEC-1", 
        state = state, 
        config = peripheral_config,
    )
    
    # Initialize and setup manager
    print("Initializing...")
    manager.initialize()
    print("Setting up...")
    manager.setup()

    # Check for loop
    if args.loop:
        loop = True
    else:
        loop = False

    # Loop forever
    while True:

        # Check if updating
        if args.update:
            print("Updating...")
            manager.update()

        # Check if resetting
        if args.reset:
            print("Resetting...")
            manager.reset()

        # Check if updating
        if args.shutdown:
            print("Shutting down...")
            manager.shutdown()

        # Check for new command if loop enabled
        if loop:
            new_command = input("New command: ")
            args = parser.parse_args(shlex.split(new_command))
        else:
            break
