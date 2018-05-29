# Import standard python libraries
import sys, argparse, logging

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
parser.add_argument("-c", "--channel", type=int)
parser.add_argument("-v", "--value", type=int)
parser.add_argument("--logging", action="store_true")
parser.add_argument("--status", action="store_true")
parser.add_argument("--edu1", action="store_true")
parser.add_argument("--on", action="store_true")
parser.add_argument("--off", action="store_true")

if __name__ == "__main__":

	# Read in arguments
	args = parser.parse_args()

	# Check for logger
	if args.logging:
		logging.basicConfig(level=logging.DEBUG)

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

	# Check if turning device on
	if args.on:
		print("Turning all channel on")
		outputs = {0: 100, 1: 100, 2: 100, 3: 100, 4: 100, 5: 100, 6: 100, 7: 100}
		error = dac5578_core.set_outputs(outputs)

	# Check if turning device off
	if args.off:
		print("Turning all channel on")
		outputs = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
		error = dac5578_core.set_outputs(outputs) 
