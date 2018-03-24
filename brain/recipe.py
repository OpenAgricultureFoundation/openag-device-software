# Import python modules
import logging, time, threading

# Import all possible states & errors
from states import States
from errors import Errors


class Recipe:
    """ Recipe handler. Manages recipe state machine and interactions
    	with recipe table in database. """

    # Initialize logger
    logger = logging.getLogger(__name__)

    # Initialize state and error lists
    states = States()
    errors = Errors()

    # Initialize state & error variables
    _state = None
    _error = None