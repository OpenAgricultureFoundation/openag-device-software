""" Description of what file does. """

# Import python modules
import logging, time

# Define environment class
class System(object):
    """ Description """

    # Initialize logger
    logger = logging.getLogger(__name__)

    # Initialize system states
    BOOT = "Boot"
    INIT = "Initialization"
    NOS = "Normal Operation"
    CONFIG = "Configuration"
    ERROR = "Error"

    # Initialize peripheral states
    WARMING = "Warming up"

    # Initialize system variables
    _prev_state = BOOT
    _state = INIT
    peripheral = {}

    # Initialize class
    def __init__(self):
        """ Description. """
        pass

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    @property
    def prev_state(self):
        return self._prev_state

    @prev_state.setter
    def prev_state(self, value):
        self._prev_state = value

    def log(self):
        self.logger.info("System prev_state: {}, state: {}".format(self.prev_state, self.state))
        self.logger.info("Peripheral state: {}".format(self.peripheral))