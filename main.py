""" Main entry point to run the application for running recipes, reading 
sensors, setting actuators, managing control loops, syncing data, and managing
external events. 

Main starts a state machine which spawns threads to do the above tasks.
Threads comminicate with each other via the shared memory `state` object`.
"""

# Import state machine
from device.device import Device

# Setup logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup connection to djando app
import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()


# Run main
if __name__ == "__main__":
	device = Device()
	device.run()