# Import standard python libraries
import sys, os, json, argparse, logging, time, shlex

# Import driver module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.led_dac5578.array import LEDArray
except:
    # ... if running tests from same dir as dac5578.py
    sys.path.append("../../../")
    from device.peripherals.led_dac5578.array import LEDArray

# Import device utilities
from device.utilities.logger import Logger

# Change directory for importing files
os.chdir("../../../")

# Setup parser
parser = argparse.ArgumentParser(description="Test and debug LED array hardware")
parser.add_argument("--edu1", action="store_true", help="specifies edu config")
parser.add_argument("--smhz1", action="store_true", help="specifies edu config")
parser.add_argument("--debug", action="store_true", help="sets logger in debug mode")
parser.add_argument("--info", action="store_true", help="sets logger in info mode")
parser.add_argument("--loop", action="store_true", help="loops command line prompt")
parser.add_argument("--reset", action="store_true", help="resets LED array")
parser.add_argument("--shutdown", action="store_true", help="shutsdown LED array")
parser.add_argument("-c", "--channel", type=str, help="specifies channel name")
parser.add_argument("-v", "--value", type=float, help="specifies output value (0-100)")
parser.add_argument("--on", action="store_true", help="turns on LEDs, can specify channel")
parser.add_argument("--off", action="store_true", help="turns off LEDs, can specify channel")
parser.add_argument("--fade", action="store_true", help="fades LEDs, can specify channel")
parser.add_argument("-s", "--spectrum", type=str, help="sets SPD spectrum from name in data/spectrums")
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

    # Initialize core
    if args.edu1:
        print("Configuring for pfc-edu v1.0")
        peripheral_setup = json.load(open("device/peripherals/led_dac5578/setups/taurus.json"))
        channel_configs = peripheral_setup["channel_configs"]
        device_config = json.load(open("data/devices/edu1.json"))
        panel_configs = device_config["peripherals"][0]["parameters"]["communication"]["panels"]
        array = LEDArray("EDU1", panel_configs, channel_configs)
    elif args.smhz1:
        print("Configuring for small-hazelnut v1.0")
        peripheral_setup = json.load(open("device/peripherals/led_dac5578/setups/orion.json"))
        channel_configs = peripheral_setup["channel_configs"]
        device_config = json.load(open("data/devices/smhz1.json"))
        panel_configs = device_config["peripherals"][0]["parameters"]["communication"]["panels"]
        array = LEDArray("SMHZ1", panel_configs, channel_configs)
    else:
        print("Please specify a device configuraion")
        sys.exit(0)

    # Check if looping
    if args.loop:
        loop = True
    else:
        loop = False

    # Optionally loop command inputs
    first = True
    while True:

        # Check if new command
        if not first:
            args = parser.parse_args(shlex.split(new_command))
        first = False

        # Check if resetting
        if args.reset:
            print("Resetting")
            array.reset()
            print("Reset successful")

        # Check if shutting down
        elif args.shutdown:
            print("Shutting down")
            array.shutdown()
            print("Shutdown successful")

        # Check if setting a channel to a value
        elif args.channel != None and args.value != None:
            print("Setting channel {} to {}%".format(args.channel, args.value))
            error = array.set_output(args.channel, args.value)
            if error.exists():
                print("Error: {}".format(error.trace))

        # Check if turning device on
        elif args.on:
            print("Turning on {channel}".format(channel = "all channels" if \
                args.channel == None else "channel: " + str(args.channel)))
            error = array.turn_on(channel_name=args.channel)
            if error.exists():
                print("Error: {}".format(error.trace))

        # Check if turning device off
        elif args.off:
            print("Turning off {channel}".format(channel = "all channels" if \
                args.channel == None else "channel: " + str(args.channel)))
            error = array.turn_off(channel_name=args.channel)
            if error.exists():
                print("Error: {}".format(error.trace))

        # Check if fading
        elif args.fade:
            print("Fading {channel}".format(channel = "all channels" if args.channel == None else "channel: " + str(args.channel)))
            error = array.fade(cycles=10, channel_name=args.channel)
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
            channel_outputs, output_spectrum, output_intensity, error = array.set_spd(
                desired_distance_cm = distance, 
                desired_intensity_watts = intensity, 
                desired_spectrum_nm_percent = spectrum,
            )
            print("Channel outputs (%): {}".format(channel_outputs))
            print("Output spectrum (%): {}".format(output_spectrum))
            print("Output intensity: {} Watts".format(output_intensity))


        # Check for new command if looping
        if loop:
            new_command = input("New command: ")
        else:
            break