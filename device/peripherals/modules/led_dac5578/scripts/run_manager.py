# Import standard python libraries
import sys, os, json, argparse, logging, time, shlex

# Import driver module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.led_dac5578.manager import LEDDAC5578
except:
    # ... if running tests from same dir as manager.py
    sys.path.append("../../../")
    from device.peripherals.led_dac5578.manager import LEDDAC5578

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.modes import Modes

# Import device state
from device.state import State

# Initialize state
state = State()

# Change directory for importing files
os.chdir("../../../")

# Setup parser
parser = argparse.ArgumentParser(description="Test and debug LED led_dac5578 hardware")
parser.add_argument("--edu1", action="store_true", help="specifies edu config")
parser.add_argument("--smhz1", action="store_true", help="specifies edu config")
parser.add_argument("--debug", action="store_true", help="sets logger in debug mode")
parser.add_argument("--info", action="store_true", help="sets logger in info mode")
parser.add_argument("--loop", action="store_true", help="loops command line prompt")
parser.add_argument("--reset", action="store_true", help="resets LED led_dac5578")
parser.add_argument("--shutdown", action="store_true", help="shutsdown LED led_dac5578")
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
        device_config = json.load(open("data/devices/edu1.json"))
        peripheral_config = device_config["peripherals"][0]
        led_dac5578 = LEDDAC5578("SMHZ1", state, peripheral_config)
    elif args.smhz1:
        print("Configuring for small-hazelnut v1.0")
        device_config = json.load(open("data/devices/smhz1.json"))
        peripheral_config = device_config["peripherals"][0]
        led_dac5578 = LEDDAC5578("SMHZ1", state, peripheral_config)
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
            led_dac5578.reset()
            print("Reset successful")

        # Check if shutting down
        elif args.shutdown:
            print("Shutting down")
            led_dac5578.shutdown()
            print("Shutdown successful")

        # Check if setting a channel to a value
        elif args.channel != None and args.value != None:
            print("Setting channel {} to {}%".format(args.channel, args.value))
            error = led_dac5578.set_output(args.channel, args.value)
            if error.exists():
                print("Error: {}".format(error.trace))

        # Check if turning device on
        elif args.on:
            print("Turning on {channel}".format(channel = "all channels" if \
                args.channel == None else "channel: " + str(args.channel)))
            led_dac5578.mode = Modes.MANUAL
            led_dac5578.process_event({"type": "Turn On"})
            if led_dac5578.response["status"] != 200:
                print("Error: {}".format(led_dac5578.response["message"]))

        # Check if turning device off
        elif args.off:
            print("Turning off {channel}".format(channel = "all channels" if \
                args.channel == None else "channel: " + str(args.channel)))
            led_dac5578.mode = Modes.MANUAL
            led_dac5578.process_event({"type": "Turn Off"})
            if led_dac5578.response["status"] != 200:
                print("Error: {}".format(led_dac5578.response["message"]))

        # Check if fading
        elif args.fade:
            print("Fading {channel}".format(channel = "all channels" if \
                args.channel == None else "channel: " + str(args.channel)))
            led_dac5578.mode = Modes.MANUAL
            led_dac5578.process_event({"type": "Fade"})

            print("did this return?")
            if led_dac5578.response["status"] != 200:
                print("Error: {}".format(led_dac5578.response["message"]))
            else:
                print(led_dac5578.response["message"])
        
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
            channel_outputs, output_spectrum, output_intensity, error = led_dac5578.set_spd(
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