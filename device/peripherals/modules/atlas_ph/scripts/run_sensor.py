# Import standard python libraries
import sys, os, json, argparse, logging, time, shlex

# Import sensor module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.modules.atlas_ph.sensor import AtlasPHSensor
except:
    # ... if running tests from same dir as sensor.py
    os.chdir("../../../../")
    from device.peripherals.modules.atlas_ph.sensor import AtlasPHSensor

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.accessors import get_peripheral_config

# Setup parser
parser = argparse.ArgumentParser(description="Test and debug sensor")
parser.add_argument("--debug", action="store_true", help="set logger in debug mode")
parser.add_argument("--info", action="store_true", help="set logger in info mode")
parser.add_argument("--loop", action="store_true", help="loop command prompt")

# Configs
parser.add_argument("--edu1", action="store_true", help="specify edu v1.0 config")

# Functions
parser.add_argument("-i", "--initialize", action="store_true", help="initialize sensor")
parser.add_argument("-s", "--setup", action="store_true", help="setup sensor")
parser.add_argument("-p", "--probe", action="store_true", help="probe sensor")
parser.add_argument("-r", "--reset", action="store_true", help="reset sensor")
parser.add_argument("-ph", "--read-ph", action="store_true", help="read pH")

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

    # Initialize config
    if args.edu1:
        print("Configuring for pfc-edu v1.0")
        filepath = "data/devices/edu1.json"
    else:
        print("Please specify a device configuraion")
        sys.exit(0)

    # Initialize sensor
    device_config = json.load(open(filepath))
    peripheral_config = get_peripheral_config(device_config["peripherals"], "AtlasPH-1")
    sensor = AtlasPHSensor(
        name = "AtlasPH-1", 
        bus = peripheral_config["parameters"]["communication"]["bus"], 
        address = int(peripheral_config["parameters"]["communication"]["address"], 16), 
        mux = int(peripheral_config["parameters"]["communication"]["mux"], 16), 
        channel = peripheral_config["parameters"]["communication"]["channel"],
    )

    # Check for loop
    if args.loop:
        loop = True
    else:
        loop = False

    # Loop forever
    while True:

        # Check if initializing
        if args.initialize:
            print("Initalizing sensor")
            error = sensor.initialize()
            if error.exists():
                print("Error: {}".format(error.trace))
            else:
                print("Sensor initialized!")

        # Check if setting up
        if args.setup:
            print("Setting up sensor")
            error = sensor.initialize()
            if error.exists():
                print("Error: {}".format(error.trace))
            else:
                print("Sensor setup!")

        # Check if probing
        elif args.probe:
            print("Probing sensor")
            error = sensor.probe()
            if error.exists():
                print("Error: {}".format(error.trace))
            else:
                print("Sensor is active!")

        # Check if resetting
        elif args.reset:
            print("Resetting sensor")
            sensor.reset()
            print("Sensor reset!")

        # Check if reading pH
        elif args.read_ph:
            print("Reading pH")
            ph, error = sensor.read_potential_hydrogen()
            if error.exists():
                print("Error: {}".format(error.trace))
            else:
                print("pH: {}".format(ph))

        # Check for new command if loop enabled
        if loop:
            new_command = input("New command: ")
            args = parser.parse_args(shlex.split(new_command))
        else:
            break
