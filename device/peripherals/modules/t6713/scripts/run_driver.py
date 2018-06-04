# Import standard python libraries
import sys, os, json, argparse, logging, time, shlex

# Import driver module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.modules.t6713.driver import T6713Driver
except:
    # ... if running tests from same dir as driver.py
    os.chdir("../../../../")
    from device.peripherals.modules.t6713.driver import T6713Driver

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.accessors import get_peripheral_config

# Setup parser basics
parser = argparse.ArgumentParser(description="Test and debug driver")
parser.add_argument("--debug", action="store_true", help="set logger in debug mode")
parser.add_argument("--info", action="store_true", help="set logger in info mode")
parser.add_argument("--loop", action="store_true", help="loop command prompt")

# Setup parser configs
parser.add_argument("--edu1", action="store_true", help="specify edu v1.0 config")

# Setup parser functions
parser.add_argument("--status", action="store_true", help="read status")
parser.add_argument("--co2", action="store_true", help="read carbon dioxide")


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

    # Initialize driver
    device_config = json.load(open(filepath))
    peripheral_config = get_peripheral_config(device_config["peripherals"], "T6713-1")        
    driver = T6713Driver(
        name = "T6713-1", 
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

        # Check if reading status
        if args.status:
            print("Reading status")
            status, error = driver.read_status()
            if error.exists():
                print("Error: {}".format(error.trace))
            else:
                print("Status: {}".format(status))

        # Check if reading carbon dioxide
        elif args.co2:
            print("Reading carbon dioxide")
            co2, error = driver.read_carbon_dioxide()
            if error.exists():
                print("Error: {}".format(error.trace))
            else:
                print("Co2: {} ppm".format(co2))

        # Check for new command if loop enabled
        if loop:
            new_command = input("New command: ")
            args = parser.parse_args(shlex.split(new_command))
        else:
            break
