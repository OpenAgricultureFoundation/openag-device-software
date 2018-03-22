""" Description of what this file does. """

# Import python modules
import json, time

# Setup logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Try to import models shared with api
try:
	from core.models import *
except:
	logger.warning("Unable to import models. Make sure api is running.")


# Run main
if __name__ == "__main__":
	# Load in configuration file
	logger.info("Loading in configuration file")
	config = json.load(open('config.json'))

	# Create environment object
	from environment import Environment
	env = Environment()

	# Create system object
	from system import System
	sys = System()

	# Create peripheral objects from config
	logger.info("Creating peripheral objects")
	peripheral = {}
	for peripheral_name in config:
		# Extract module parameters from config
		module_name = "peripherals." + config[peripheral_name]["class_file"]
		class_name = config[peripheral_name]["class_name"]

		# Import peripheral library
		module_instance= __import__(module_name, fromlist=[class_name])
		class_instance = getattr(module_instance, class_name)

		# Create peripheral object instances
		peripheral[peripheral_name] = class_instance(config=config[peripheral_name]["class_config"], name=peripheral_name)

	# Run peripheral objects
	logger.info("Running peripheral object threads")
	for peripheral_name in peripheral:
		peripheral[peripheral_name].run(env)