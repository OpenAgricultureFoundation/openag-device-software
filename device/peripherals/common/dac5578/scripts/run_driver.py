# Import standard python libraries
import sys, os, json, argparse, logging, time, shlex

# Get current working directory
cwd = os.getcwd()
print("Running from: {}".format(cwd))

# Set correct import path
if cwd.endswith("dac5578"):
    print("Running locally")
    sys.path.append("../../../../")
elif cwd.endswith("openag-device-software"):
    print("Running globally")
else:
    print("Running from invalid location")
    sys.exit(0)

from device.peripherals.common.dac5578.driver import DAC5578

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.accessors import get_peripheral_config

# Set directory for loading files
if cwd.endswith("dac5578"):
    os.chdir("../../../../")

# Setup parser basics
parser = argparse.ArgumentParser(description="Test and debug driver")
parser.add_argument("--debug", action="store_true", help="set logger in debug mode")
parser.add_argument("--info", action="store_true", help="set logger in info mode")
parser.add_argument("--loop", action="store_true", help="loop command prompt")

# Setup parser configs
parser.add_argument("--device", type=str, help="specifies device config file name")
parser.add_argument("--name", type=str, help="specifies peripheral name in config")
parser.add_argument("--panel-name", type=str, help="specifies panel name in config")

# Setup parser functions
parser.add_argument("--probe", action="store_true", help="probes device")
parser.add_argument("-c", "--channel", type=int, help="sets channel (0-7)")
parser.add_argument("-p", "--percent", type=int, help="sets output percent (0-100)")
parser.add_argument("--high", action="store_true", help="outputs high voltage")
parser.add_argument("--low", action="store_true", help="outputs low voltage")
parser.add_argument("--fade", action="store_true", help="fades voltage x10 times")
parser.add_argument("--reset", action="store_true", help="resets device")

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
    communication = peripheral_config["parameters"]["communication"]

    # Check is dac is used in led panel
    if "panels" in communication:

        # Default to using first panel in communication list
        communication = communication["panels"][0]

        # Check if panel name is specified
        if args.panel_name != None:

            # Check if panel name exists in list
            name = None
            for entry in communication["panels"]:
                if entry["name"] == args.panel_name:
                    communication = entry
                    name = entry["name"]
                    break

            # Check if panel name was found
            if name == None:
                print(
                    "Unable to find panel named `{}`, using first entry instead".format(
                        args.panel_name
                    )
                )

    # Initialize driver optional mux parameter
    mux = communication.get("mux", None)
    if mux != None:
        mux = int(mux, 16)

    # Initialize driver
    driver = DAC5578(
        name=args.name,
        bus=communication["bus"],
        address=int(communication["address"], 16),
        mux=mux,
        channel=communication.get("channel", None),
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
            print("Probing")
            error = driver.probe()
            if error.exists():
                print("error = {}".format(error.trace))
            else:
                print("Probe successful")

        # Check if setting a channel to a value
        elif args.channel != None and args.percent != None:
            print("Setting channel {} to {}%".format(args.channel, args.percent))
            error = driver.write_output(args.channel, args.percent)
            if error.exists():
                print("Error: {}".format(error.trace))

        # Check if setting all channels to a value
        elif args.channel == None and args.percent != None:
            print("Setting all channels to {}%".format(args.percent))

            outputs = {}
            for i in range(8):
                outputs[i] = args.percent

            error = driver.write_outputs(outputs)
            if error.exists():
                print("Error: {}".format(error.trace))

        # Check if setting a channel or all channels high
        elif args.high:
            print(
                "Setting {channel} high".format(
                    channel="all channels"
                    if args.channel == None
                    else "channel: " + str(args.channel)
                )
            )
            error = driver.set_high(channel=args.channel)
            if error.exists():
                print("Error: {}".format(error.trace))

        # Check if setting a channel or all channels low
        elif args.low:
            print(
                "Setting {channel} low".format(
                    channel="all channels"
                    if args.channel == None
                    else "channel: " + str(args.channel)
                )
            )
            error = driver.set_low(channel=args.channel)
            if error.exists():
                print("Error: {}".format(error.trace))

        # Check if fading
        elif args.fade:
            print(
                "Fading {channel}".format(
                    channel="all channels"
                    if args.channel == None
                    else "channel: " + str(args.channel)
                )
            )
            error = driver.fade(cycles=10, channel=args.channel)
            if error.exists():
                print("Error: {}".format(error.trace))

        # Check if resetting
        elif args.reset:
            print("Resetting")
            driver.reset()
            print("Reset successful")

        # Check for new command if loop enabled
        if loop:
            new_command = input("New command: ")
            args = parser.parse_args(shlex.split(new_command))
        else:
            break
