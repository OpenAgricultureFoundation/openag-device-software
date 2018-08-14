# Import standard python libraries
import sys, os, json, argparse, logging, time, shlex

# Get current working directory
cwd = os.getcwd()
print("Running from: {}".format(cwd))

# Set correct import path
if cwd.endswith("sht25"):
    print("Running locally")
    sys.path.append("../../../../")
elif cwd.endswith("openag-device-software"):
    print("Running globally")
else:
    print("Running from invalid location")
    sys.exit(0)

# Import driver
from device.peripherals.modules.sht25.driver import SHT25Driver

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.accessors import get_peripheral_config

# Set directory for loading files
os.chdir("../../../../")

# Setup parser basics
parser = argparse.ArgumentParser(description="Test and debug hardware")
parser.add_argument("--debug", action="store_true", help="set logger in debug mode")
parser.add_argument("--info", action="store_true", help="set logger in info mode")
parser.add_argument("--loop", action="store_true", help="loop command prompt")

# Setup parser configs
parser.add_argument("--device", type=str, help="specifies device config")

# Setup parser functions
parser.add_argument("--temperature", action="store_true", help="read temperature")
parser.add_argument("--humidity", action="store_true", help="read humidity")
parser.add_argument("--user-register", action="store_true", help="read user register")


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
        peripheral_config = get_peripheral_config(
            device_config["peripherals"], "SHT25-Top"
        )
    else:
        print("Please specify a device configuraion")
        sys.exit(0)

    # Initialize driver
    driver = SHT25Driver(
        name="SHT25-Top",
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

        # Check if reading temperature
        if args.temperature:
            print("Reading temperature")
            temperature, error = driver.read_temperature()
            if error.exists():
                print("Error: {}".format(error.trace))
            else:
                print("Temperature: {} C".format(temperature))

        # Check if reading humidity
        elif args.humidity:
            print("Reading humidity")
            humidity, error = driver.read_humidity()
            if error.exists():
                print("Error: {}".format(error.trace))
            else:
                print("Humidity: {} %".format(humidity))

        # Check if reading user register
        elif args.user_register:
            print("Reading user register")
            user_register, error = driver.read_user_register()
            if error.exists():
                print("Error: {}".format(error.trace))
            else:
                print("User Register: {}".format(user_register))

        # Check for new command if loop enabled
        if loop:
            new_command = input("New command: ")
            args = parser.parse_args(shlex.split(new_command))
        else:
            break
