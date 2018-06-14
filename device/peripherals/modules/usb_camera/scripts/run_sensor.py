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

# Import sensor
from device.peripherals.modules.usb_camera.sensor import USBCameraSensor

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.accessors import get_peripheral_config

# Set directory for loading files
if cwd.endswith("usb_camera"):
    os.chdir("../../../../")

# Setup parser basics
parser = argparse.ArgumentParser(description="Test and debug camear")
parser.add_argument("--debug", action="store_true", help="set logger in debug mode")
parser.add_argument("--info", action="store_true", help="set logger in info mode")
parser.add_argument("--loop", action="store_true", help="loop command prompt")

# Setup parser cnfigs
parser.add_argument("--device", type=str, help="specifies device config")

# Setup parser functions
parser.add_argument("--probe", action="store_true", help="probes camera")
parser.add_argument("--capture", action="store_true", help="captures an image")
parser.add_argument("--reset", action="store_true", help="reset camera")


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
        setup_dict = json.load(open("device/peripherals/modules/usb_camera/setups/elp_usb500w02ml21.json"))
    else:
        print("Please specify a device configuraion")
        sys.exit(0)

    # Initialize sensor
    directory = "device/peripherals/modules/usb_camera/scripts/images/"
    camera = USBCameraSensor(
        name = "Camera-1", 
        directory = directory,
        vendor_id = setup_dict["properties"]["vendor_id"],
        product_id = setup_dict["properties"]["product_id"],
        resolution = setup_dict["properties"]["resolution"],
    )

    # Check for loop
    if args.loop:
        loop = True
    else:
        loop = False

    # Loop forever
    while True:

        # Check if probing
        if args.probe:
            print("Probing camera")
            error = camera.probe()
            if error.exists():
                print("Error: {}".format(error.trace))
            else:
                print("Probe successful!")

        # Check if capturing image
        elif args.capture:
            print("Capturing image")
            error = camera.capture()
            if error.exists():
                print("Error: {}".format(error.trace))
            else:
                print("Successfully captured image!")

        # Check if resetting
        elif args.reset:
            print("Resetting camera")
            camera.reset()
            print("camera reset!")

        # Check for new command if loop enabled
        if loop:
            new_command = input("New command: ")
            args = parser.parse_args(shlex.split(new_command))
        else:
            break
