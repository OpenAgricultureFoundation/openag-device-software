# Import standard python libraries
import sys, argparse, logging, time

# Import driver module...
try:
	# ... if running tests from project root
	sys.path.append(".")
	from device.drivers.dac5578.core import DAC5578Core
except:
	# ... if running tests from same dir as dac5578.py
	sys.path.append("../../../")
	from device.drivers.dac5578.core import DAC5578Core


# Import device utilities
from device.utilities.logger import Logger

# Setup parser
parser = argparse.ArgumentParser(description="Run dac5578 core.")
parser.add_argument("--edu1", action="store_true")
parser.add_argument("--debug", action="store_true")
parser.add_argument("--info", action="store_true")
parser.add_argument("--status", action="store_true")
parser.add_argument("-c", "--channel", type=int)
parser.add_argument("-v", "--value", type=int)


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
		dac5578_core = DAC5578Core("Test", 2, 0x47, 0x77, 3)
	else:
		print("Please specify a device configuraion")
		sys.exit(0)

	# Check if reading status
	if args.status:
		print("Reading status")
		powered, error = dac5578_core.read_power_register()
		if error.exists():
			print("error = {}".format(error.trace))
		else:
			print("powered = {}".format(powered))
			sys.exit(0)

	# Check if setting a channel to a value
	if args.channel != None and args.value != None:
		print("Setting channel {} to {}%".format(args.channel, args.value))
		error = dac5578_core.set_output(args.channel, args.value)
		if error.exists():
			print("Error: {}".format(error.trace))
		sys.exit(0)


