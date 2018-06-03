# Import standard python libraries
import sys, os, json, argparse, logging, time, shlex

# Import driver module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.modules.sht25.driver import SHT25Driver
except:
    # ... if running tests from same dir as driver.py
    os.chdir("../../../../")
    from device.peripherals.modules.sht25.driver import SHT25Driver

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.accessors import get_peripheral_config

# Setup parser basics
parser = argparse.ArgumentParser(description="Test and debug AtlasEC hardware")
parser.add_argument("--debug", action="store_true", help="set logger in debug mode")
parser.add_argument("--info", action="store_true", help="set logger in info mode")
parser.add_argument("--loop", action="store_true", help="loop command prompt")

# Setup parser configs
parser.add_argument("--edu1", action="store_true", help="specify edu v1.0 config")

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


    # Initialize config
    if args.edu1:
        print("Configuring for pfc-edu v1.0")
        filepath = "data/devices/edu1.json"
    else:
        print("Please specify a device configuraion")
        sys.exit(0)

    # Initialize driver
    device_config = json.load(open(filepath))
    peripheral_config = get_peripheral_config(device_config["peripherals"], "SHT25-1")        
    driver = SHT25Driver(
        name = "SHT25-1", 
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
