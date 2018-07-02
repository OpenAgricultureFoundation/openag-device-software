# Import standard python libraries
import sys, os, json, argparse, logging, time, shlex

# Get current working directory
cwd = os.getcwd()
print("Running from: {}".format(cwd))

# Set correct import path
if cwd.endswith("ccs811"):
    print("Running locally")
    sys.path.append("../../../../")
elif cwd.endswith("openag-device-software"):
    print("Running globally")
else:
    print("Running from invalid location")
    sys.exit(0)

# Import driver
from device.peripherals.modules.ccs811.driver import CCS811Driver

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.accessors import get_peripheral_config

# Setup parser basics
parser = argparse.ArgumentParser(description="Test and debug driver")
parser.add_argument("--debug", action="store_true", help="set logger in debug mode")
parser.add_argument("--info", action="store_true", help="set logger in info mode")
parser.add_argument("--loop", action="store_true", help="loop command prompt")

# Setup parser configs
parser.add_argument("--device", type=str, help="specifies device config")

# Setup parser functions
parser.add_argument("--co2", action="store_true", help="read co2")
parser.add_argument("--tvoc", action="store_true", help="read tvoc")
parser.add_argument("--mode", type=int, help="set device mode 1-4")


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
        os.chdir("../../../../")
        print("Using device config: {}".format(args.device))
        device_config = json.load(open("data/devices/{}.json".format(args.device)))
        peripheral_config = get_peripheral_config(
            device_config["peripherals"], "CCS811-Top"
        )
    else:
        print("Please specify a device configuraion")
        sys.exit(0)

    # Initialize driver
    driver = CCS811Driver(
        name="CCS811-Top",
        bus=peripheral_config["parameters"]["communication"]["bus"],
        address=int(peripheral_config["parameters"]["communication"]["address"], 16),
        mux=int(peripheral_config["parameters"]["communication"]["mux"], 16),
        channel=peripheral_config["parameters"]["communication"]["channel"],
    )

    # Check for loop
    if args.loop:
        loop = True
    else:
        loop = False

    # Loop forever
    while True:

        # Check if setting measurement mode
        if args.mode != None:
            print("Setting measurement mode")
            try:
                driver.write_measurement_mode(args.mode, False, False, retry=True)
            except Exception as e:
                print("Error: {}".format(e))

        # Check if reading co2/tvoc
        if args.co2 or args.tvoc:
            print("Reading co2/tvoc")
            try:
                co2, tvoc = driver.read_algorithm_data(retry=True)
                print("CO2: {} ppm".format(co2))
                print("TVOC: {} ppm".format(tvoc))
            except Exception as e:
                print("Error: {}".format(e))

        # Check for new command if loop enabled
        if loop:
            new_command = input("New command: ")
            args = parser.parse_args(shlex.split(new_command))
        else:
            break
