# Import standard python libraries
import sys, argparse, logging, time, shlex

# Import driver module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.modules.atlas_ec.driver import AtlasECDriver
except:
    # ... if running tests from same dir as driver.py
    sys.path.append("../../../../")
    from device.peripherals.modules.atlas_ec.driver import AtlasECDriver

# Import device utilities
from device.utilities.logger import Logger

# Setup parser
parser = argparse.ArgumentParser(description="Test and debug AtlasEC hardware")
parser.add_argument("--debug", action="store_true", help="set logger in debug mode")
parser.add_argument("--info", action="store_true", help="set logger in info mode")
parser.add_argument("--loop", action="store_true", help="loop command prompt")

# Configs
parser.add_argument("--edu1", action="store_true", help="specify edu v1.0 config")

# Functions
parser.add_argument("-p", "--probe", action="store_true", help="probe sensor")
parser.add_argument("-i", "--read-info", action="store_true", help="read sensor info")
parser.add_argument("-s", "--read-status", action="store_true", help="read sensor status")
parser.add_argument("-ec", "--read-ec", action="store_true", help="read electrical conductivity")


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
        driver = AtlasECDriver("Test", 2, 0x64, mux=0x77, channel=4)
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

        # Check if probing
        if args.probe:
            print("Probing")
            error = driver.probe()
            if error.exists():
                print("error = {}".format(error.trace))
            else:
                print("Probe successful")

        # Check if reading info
        elif args.read_info:
            print("Reading info")
            sensor_type, firmware_version, error = driver.read_info()
            if error.exists():
                print("Error: {}".format(error.trace))
            else:
                print("Sensor type: {}".format(sensor_type))
                print("Firmware version: {}".format(firmware_version))

        # Check if reading status
        elif args.read_status:
            print("Reading status")
            prev_restart_reason, voltage, error = driver.read_status()
            if error.exists():
                print("Error: {}".format(error.trace))
            else:
                print("Prev restart reason: {}".format(prev_restart_reason))
                print("Voltage: {}".format(voltage))

        # Check if reading electrical conductivity
        elif args.read_ec:
            print("Reading electrical conductivity")
            ec, error = driver.read_electrical_conductivity()
            if error.exists():
                print("Error: {}".format(error.trace))
            else:
                print("EC: {} mS/cm".format(ec))

        # Check for new command if loop enabled
        if loop:
            new_command = input("New command: ")
            args = parser.parse_args(shlex.split(new_command))
        else:
            break