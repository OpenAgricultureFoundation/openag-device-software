# Import standard python libraries
import sys, os, json, argparse, logging, time, shlex

# Import driver module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.modules.led_dac5578.panel import LEDDAC5578Panel
except:
    # ... if running tests from same dir as dac5578.py
    os.chdir("../../../../")
    from device.peripherals.modules.led_dac5578.panel import LEDDAC5578Panel

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.accessors import get_peripheral_config

# Setup parser basics
parser = argparse.ArgumentParser(description="Test and debug panel")
parser.add_argument("--debug", action="store_true", help="set logger in debug mode")
parser.add_argument("--info", action="store_true", help="set logger in info mode")
parser.add_argument("--loop", action="store_true", help="loop command prompt")

# Setup parser configs
parser.add_argument("--device", type=str, help="specifies device config")

# Setup parser functions
parser.add_argument("--reset", action="store_true", help="resets LED Panel")
parser.add_argument("--shutdown", action="store_true", help="shutsdown LED Panel")
parser.add_argument("-c", "--channel", type=str, help="specifies channel name")
parser.add_argument("-v", "--value", type=float, help="specifies output value (0-100)")
parser.add_argument(
    "--on", action="store_true", help="turns on LEDs, can specify channel"
)
parser.add_argument(
    "--off", action="store_true", help="turns off LEDs, can specify channel"
)
parser.add_argument(
    "--fade", action="store_true", help="fades LEDs, can specify channel"
)
parser.add_argument(
    "-s", "--spectrum", type=str, help="sets SPD spectrum from name in data/spectrums"
)
parser.add_argument("-i", "--intensity", type=float, help="sets SPD intensity in Watts")
parser.add_argument("-d", "--distance", type=float, help="sets SPD distance in cm")


if __name__ == "__main__":

    # Read in arguments
    args = parser.parse_args()

    # Check for logger
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
            device_config["peripherals"], "LEDPanel-Top"
        )
    else:
        print("Please specify a device configuraion")
        sys.exit(0)

    # Initialize panel parameters
    setup_name = peripheral_config["parameters"]["setup"]["file_name"]
    setup_dict = json.load(open("device/peripherals/modules/" + setup_name + ".json"))

    # Initialize panel
    panel = LEDDAC5578Panel(
        name=peripheral_config["parameters"]["communication"]["panels"][0]["name"],
        channel_configs=setup_dict["channel_configs"],
        bus=peripheral_config["parameters"]["communication"]["panels"][0]["bus"],
        address=int(
            peripheral_config["parameters"]["communication"]["panels"][0]["address"], 16
        ),
        mux=int(
            peripheral_config["parameters"]["communication"]["panels"][0]["mux"], 16
        ),
        channel=peripheral_config["parameters"]["communication"]["panels"][0][
            "channel"
        ],
    )

    # Check for loop
    if args.loop:
        loop = True
    else:
        loop = False

    # Loop forever
    while True:

        # Check if resetting
        if args.reset:
            print("Resetting")
            panel.reset()
            print("Reset successful")

        # Check if shutting down
        elif args.shutdown:
            print("Shutting down")
            panel.shutdown()
            print("Shutdown successful")

        # Check if setting a channel to a value
        elif args.channel != None and args.value != None:
            print("Setting channel {} to {}%".format(args.channel, args.value))
            error = panel.set_output(args.channel, args.value)
            if error.exists():
                print("Error: {}".format(error.trace))

        # Check if turning device on
        elif args.on:
            print(
                "Turning on {channel}".format(
                    channel="all channels"
                    if args.channel == None
                    else "channel: " + str(args.channel)
                )
            )
            error = panel.turn_on(channel_name=args.channel)
            if error.exists():
                print("Error: {}".format(error.trace))

        # Check if turning device off
        elif args.off:
            print(
                "Turning off {channel}".format(
                    channel="all channels"
                    if args.channel == None
                    else "channel: " + str(args.channel)
                )
            )
            error = panel.turn_off(channel_name=args.channel)
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
            error = panel.fade(cycles=10, channel_name=args.channel)
            if error.exists():
                print("Error: {}".format(error.trace))

        # Check if setting spd
        elif args.spectrum != None:

            # Load spectrum
            filepath = "data/spectrums/{}.json".format(args.spectrum)
            try:
                spectrum = json.load(open(filepath))
                print("Loaded spectrum from: {}".format(filepath))
                print("Desirde spectrum: {}".format(spectrum))
            except Exception as e:
                print("Unable to load spectrum from: {}".format(filepath))
                print(e)

            # Check if intensity is specified
            if args.intensity != None:
                intensity = args.intensity
                print("Desired intensity: {} Watts".format(intensity))
            else:
                print("Intensity is required to set SPD, try 50W")
                sys.exit(0)

            # Check if distance specified
            if args.distance != None:
                distance = args.distance
                print("Desired distance: {} cm".format(distance))
            else:
                distance = channel_configs[0]["planar_distance_map"][0]["distance_cm"]
                print("Default distance (default): {} cm".format(distance))

            # Set spd
            print("Setting SPD")
            channel_outputs, output_spectrum, output_intensity, error = panel.set_spd(
                desired_distance_cm=distance,
                desired_ppfd_umol_m2_s=intensity,
                desired_spectrum_nm_percent=spectrum,
            )
            print("Channel outputs (%): {}".format(channel_outputs))
            print("Output spectrum (%): {}".format(output_spectrum))
            print("Output intensity: {} Watts".format(output_intensity))

        # Check for new command if loop enabled
        if loop:
            new_command = input("New command: ")
            args = parser.parse_args(shlex.split(new_command))
        else:
            break
