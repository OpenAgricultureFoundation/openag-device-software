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


    def __init__(self):
        """ Initializes system object. """
        self.system_state = {"reset": False}
        self.peripheral_state = {}
        self.controller_state = {}
