# Import python modules
import logging, time

# Import all possible states & errors
from device.utility.states import States
from device.utility.errors import Errors


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

    # Initialize recipe variables
    recipe_dict = None

    # Initialize state objects
    system_state = {"reset": False}
    peripheral_state = {}
    controller_state = {}
    recipe_state = {}


    def __init__(self):
        # Remove this:
        import json
        self.recipe_dict = json.load(open("device/data/recipe.json"))