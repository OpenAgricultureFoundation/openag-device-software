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


    def get_log(self, recipe=True):
        """ Returns log string of current system state. """
        log = ""

        if recipe:
            
            log += "\n    Recipe:"
            log += "\n        Name: {}".format(self.recipe_state["name"])
            log += "\n        Started: {}".format(self.recipe_state["start_datestring"])
            log += "\n        Duration: {}".format(self.recipe_state["duration_string"])
            log += "\n        Progress: {} %".format(self.recipe_state["percent_complete_string"])
            log += "\n        Phase: {}".format(self.recipe_state["phase"])
            log += "\n        Cycle: {}".format(self.recipe_state["cycle"])
            log += "\n        Environment: {}".format(self.recipe_state["environment_name"])

        return log
