# Import python modules
import logging, time

# Import all possible states & errors
from states import States
from errors import Errors


class System(object):
    """ A shared memory object used to manage the state machines 
    in each thread and signal events """

    # Initialize logger
    logger = logging.getLogger(__name__)

    # Initialize state and error lists
    states = States()
    errors = Errors()

    # Initialize system state
    state = states.CONFIG
    reset = False

    # Initialize state objects
    system_state = {"reset": False}
    peripheral_state = {}
    controller_state = {}
    recipe_state = {}