""" Main entry point to run the application for running recipes, reading 
sensors, setting actuators, managing control loops, syncing data, and managing
external events. 

Main starts a state machine which spawns threads to do the above tasks.
Threads comminicate with each other via shared memory objects for the system
and environment.

The `system` shared memory object is used to manage the state machines in each 
thread and signal events.

The `environment` shared memory object is used to report sensor data, set 
desired setpoints, and command actuators. """

import os, sys

# path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, path)


from common.models import *


# Import state machine
from device.state_machine import StateMachine

# Setup logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Run main
if __name__ == "__main__":
	state_machine = StateMachine()
	state_machine.run()