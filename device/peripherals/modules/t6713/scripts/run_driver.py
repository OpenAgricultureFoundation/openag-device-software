# Import standard python libraries
import sys, os, json, argparse, logging, time, shlex

# Get current working directory
cwd = os.getcwd()
print("Running from: {}".format(cwd))

# Set correct import path
if cwd.endswith("t6713"):
    print("Running locally")
    sys.path.append("../../../../")
elif cwd.endswith("openag-device-software"):
    print("Running globally")
else:
    print("Running from invalid location")
    sys.exit(0)

# Import driver
from device.peripherals.modules.t6713.driver import T6713Driver

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.accessors import get_peripheral_config

# Set directory for loading files
if cwd.endswith("t6713"):
    os.chdir("../../../../")

# Setup parser basics
parser = argparse.ArgumentParser(description="Test and debug driver")
parser.add_argument("--debug", action="store_true", help="set logger in debug mode")
parser.add_argument("--info", action="store_true", help="set logger in info mode")
parser.add_argument("--loop", action="store_true", help="loop command prompt")

# Setup parser configs
parser.add_argument("--device", type=str, help="specifies device config file name")
parser.add_argument("--name", type=str, help="specifies peripheral name in config")

# Setup parser functions
parser.add_argument("--status", action="store_true", help="read status")
parser.add_argument("--setup", action="store_true", help="sets up sensor")
parser.add_argument("--co2", action="store_true", help="read carbon dioxide")
parser.add_argument("--reset", action="store_true", help="resets sensor")
parser.add_argument("--enable-abc", action="store_true", help="resets sensor")
parser.add_argument("--disable-abc", action="store_true", help="resets sensor")


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
    if args.device == None:
        print("Please specify a device configuraion")
        sys.exit(0)

    # Check for peripheral name
    if args.name == None:
        print("Please specify a peripheral name")
        sys.exit(0)

    # Set device config
    print("Using device config: {}".format(args.device))
    device_config = json.load(open("data/devices/{}.json".format(args.device)))
    peripheral_config = get_peripheral_config(device_config["peripherals"], args.name)

    # Initialize driver
    driver = T6713Driver(
        name=args.name,
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

        # Check if reading status
        if args.status:
            print("Reading status")
            status = driver.read_status(retry=True)
            print("Status: {}".format(status))

        # Check if setting up sensor
        if args.setup:
            print("Setting up sensor")
            driver.setup(retry=True)

        # Check if reading carbon dioxide
        elif args.co2:
            print("Reading co2")
            co2 = driver.read_co2(retry=True)
            print("Co2: {} ppm".format(co2))

        # Check if resetting sensor
        elif args.reset:
            print("Resetting")
            driver.reset(retry=True)

        # Check if enabling abc logic
        elif args.enable_abc:
            print("Enabling abc logic")
            driver.enable_abc_logic(retry=True)

        # Check if disabling abc logic
        elif args.disable_abc:
            print("Disabling abc logic")
            driver.disable_abc_logic(retry=True)

        # Check for new command if loop enabled
        if loop:
            new_command = input("New command: ")
            args = parser.parse_args(shlex.split(new_command))
        else:
            break
