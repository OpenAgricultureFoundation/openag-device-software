# Import standard python libraries
import sys, os, json, argparse, logging, time, shlex

# Get current working directory
cwd = os.getcwd()
print("Running from: {}".format(cwd))

# Set correct import path
if cwd.endswith("usb_camera"):
    print("Running locally")
    sys.path.append("../../../../")
elif cwd.endswith("openag-device-software"):
    print("Running globally")
else:
    print("Running from invalid location")
    sys.exit(0)

# Import driver
from device.peripherals.modules.usb_camera.driver import USBCameraDriver

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.accessors import get_peripheral_config

# Set directory for loading files
if cwd.endswith("usb_camera"):
    os.chdir("../../../../")

# Setup parser basics
parser = argparse.ArgumentParser(description="Test and debug usb camera driver")
parser.add_argument("--debug", action="store_true", help="set logger in debug mode")
parser.add_argument("--info", action="store_true", help="set logger in info mode")
parser.add_argument("--loop", action="store_true", help="loop command prompt")

# Setup parser configs
parser.add_argument("--device", type=str, help="specifies device config")

# Setup parser functions
parser.add_argument("--capture", action="store_true", help="capture image")


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
            device_config["peripherals"], "Camera-Top"
        )
        setup_name = peripheral_config["parameters"]["setup"]["file_name"]
        peripheral_setup = json.load(
            open("device/peripherals/modules/" + setup_name + ".json")
        )
    else:
        print("Please specify a device configuraion")
        sys.exit(0)

    # Initialize directory
    directory = "device/peripherals/modules/usb_camera/scripts/images/"

    # Initialize driver
    driver = USBCameraDriver(
        name="Test",
        vendor_id=peripheral_setup["properties"]["vendor_id"],
        product_id=peripheral_setup["properties"]["product_id"],
        resolution=peripheral_setup["properties"]["resolution"],
        directory=directory,
    )

    # Check for loop
    if args.loop:
        loop = True
    else:
        loop = False

    # Loop forever
    while True:

        # Check if capturing image
        if args.capture:
            print("Capturing image")
            error = driver.capture()
            if error.exists():
                print("Error: {}".format(error.trace))
            else:
                print("Successfully captured image!")

        # Check for new command if loop enabled
        if loop:
            new_command = input("New command: ")
            args = parser.parse_args(shlex.split(new_command))
        else:
            break
