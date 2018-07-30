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
parser.add_argument("--setup", action="store_true", help="setup sensor")
parser.add_argument("--co2", action="store_true", help="read co2")
parser.add_argument("--tvoc", action="store_true", help="read tvoc")
parser.add_argument("--mode", type=int, help="set device mode 1-4")
parser.add_argument("--status", action="store_true", help="read status register")
parser.add_argument("--error", action="store_true", help="read error register")
parser.add_argument("--reset", action="store_true", help="resets sensor")
parser.add_argument("--check-hardware-id", action="store_true", help="checks hw id")
parser.add_argument("--start-app", action="store_true", help="starts app")


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

        # Check if setting up sensor
        if args.setup:
            print("Setting up sensor")
            driver.setup(retry=True)

        # Check if reading co2/tvoc
        elif args.co2 or args.tvoc:
            print("Reading co2/tvoc")
            try:
                co2, tvoc = driver.read_algorithm_data(retry=True)
                print("CO2: {} ppm".format(co2))
                print("TVOC: {} ppm".format(tvoc))
            except Exception as e:
                print("Error: {}".format(e))

        # Check if setting measurement mode
        elif args.mode != None:
            print("Setting measurement mode")
            try:
                driver.write_measurement_mode(args.mode, False, False, retry=True)
            except Exception as e:
                logger.exception("Unable to set measurement mode")

        # Check if reading status register
        elif args.status:
            print("Reading status register")
            try:
                status_register = driver.read_status_register(retry=True)
                print(status_register)
            except Exception as e:
                print("Error: {}".format(e))

        # Check if reading error register
        elif args.error:
            print("Reading error register")
            try:
                error_register = driver.read_error_register(retry=True)
                print(error_register)
            except Exception as e:
                print("Error: {}".format(e))

        # Check if resetting
        elif args.reset:
            print("Resetting")
            try:
                driver.reset(retry=True)
            except Exception as e:
                print("Error: {}".format(e))

        # Check if checking hardware id
        elif args.check_hardware_id:
            print("Checking hardware ID")
            try:
                driver.check_hardware_id(retry=True)
                print("Hardware ID is Valid")
            except Exception as e:
                print("Error: {}".format(e))

        # Check if starting app
        elif args.start_app:
            print("Starting app")
            try:
                driver.start_app(retry=True)
            except Exception as e:
                print("Error: {}".format(e))

        # Check for new command if loop enabled
        if loop:
            new_command = input("New command: ")
            args = parser.parse_args(shlex.split(new_command))
        else:
            break
