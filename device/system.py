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


    def get_log(self, recipe=True, thread_states=True):
        """ Returns log string of current system state. """
        log = ""

        # Create recipe log
        if recipe:
            log += "\n    Recipe:"
            log += "\n        Name: {}".format(self.recipe_state["name"])
            log += "\n        Started: {}".format(self.recipe_state["start_datestring"])
            log += "\n        Progress: {} %".format(self.recipe_state["percent_complete_string"])
            log += "\n        Time Elapsed: {}".format(self.recipe_state["time_elapsed_string"])
            log += "\n        Time Remaining: {}".format(self.recipe_state["time_remaining_string"])
            log += "\n        Phase: {}".format(self.recipe_state["phase"])
            log += "\n        Cycle: {}".format(self.recipe_state["cycle"])
            log += "\n        Environment: {}".format(self.recipe_state["environment_name"])
        
        # Create thread states log
        if thread_states:
            log += "\n    States:"
            log += "\n        System: {}".format(self.state)
            log += "\n        Recipe: {}".format(self.recipe_state["state"])
            for periph in self.peripheral_state:
                verbose_name = self.peripheral_state[periph]["verbose_name"]
                state = self.peripheral_state[periph]["state"]
                log += "\n        {}: {}".format(verbose_name, state)

        # Return log string
        return log
