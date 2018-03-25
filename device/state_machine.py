# Import python modules
import logging, time, json, threading

# Import all possible states & errors
from device.utility.states import States
from device.utility.errors import Errors

# Import shared memory objects
from device.system import System
from device.environment import Environment

# Import recipe handler
from device.recipe import Recipe


class StateMachine(object):
    """ A state machine that spawns threads to run recipes, read sensors, set 
    actuators, manage control loops, sync data, and manage external events. """

    # Initialize logger
    logger = logging.getLogger(__name__)

    # Initialize state and error lists
    states = States()
    errors = Errors()

    # Initialize configurable thread objects
    peripheral = {}
    controller = {}


    def __init__(self):
        """ Initializes state machine. """
        self.sys = System()
        self.env = Environment()

    
    def run(self):
        """ Runs state machine. """
        self.logger.info("Starting state machine")
        while True:
            if self.sys.state == self.states.CONFIG:
                self.config_state()
            elif self.sys.state == self.states.SETUP:
                self.setup_state()
            elif self.sys.state == self.states.INIT:
                self.init_state()
            elif self.sys.state == self.states.NOS:
                self.nos_state()


    def config_state(self):
        """ Runs configuration state. Loads config then transitions to 
            setup state. """
        self.logger.info("Entered CONFIG state")
        self.load_config()
        self.set_state(self.states.SETUP)


    def setup_state(self):
        """ Runs setup state. Loads stored system state, creates and spawns 
            recipe, peripheral, and controller threads, then transitions to 
            initialization state. """
        self.logger.info("Entered SETUP state")
        
        # TODO: Load in stored system state from database

        # Create and spawn threads
        self.recipe = Recipe(self.env, self.sys)
        self.recipe.spawn()
        self.create_peripherals()
        self.spawn_peripherals()
        self.sys.state = self.states.INIT


    def init_state(self):
        """ Runs initialization state. Waits for all peripherals to enter NOS, 
            WARMING, or ERROR, then transitions to normal operating state. """
        self.logger.info("Entered INIT state")
        while not self.all_peripherals_ready():
            time.sleep(0.2)
        self.sys.state = self.states.NOS


    def nos_state(self):
        """ Runs normal operation state. Transitions to reset if commanded. 
            Transitions to error state on error."""
        self.logger.info("Entered NOS state")

        while True:
            # Log environment data
            self.log_all()

            # Check for system reset
            if self.sys.reset:
                self.sys.state = self.states.RESET
                continue
            
            # Check for system error
            if self.sys.state == self.states.ERROR:
                continue

            # Update every 2 seconds
            time.sleep(2) # seconds


 
    def reset_state(self):
        """ Runs reset state. """
        time.sleep(0.1) # 100ms


    def error_state(self):
        """ Runs error state. """
        time.sleep(0.1) # 100ms


    def set_state(self, state):
        """ Safely sets state on `system` shared memory object. """
        with threading.Lock():
            self.sys.state = state


    def load_config(self):
        """ Loads configuration. """
        self.config = json.load(open('device/data/config.json'))
        # TODO: validate config


    def create_peripherals(self):
        """ Creates peripheral thread objects defined in config. """
        
        for peripheral_name in self.config["peripherals"]:
            # Extract module parameters from config
            peripheral = self.config["peripherals"][peripheral_name]
            module_name = "device.peripheral." + peripheral["class_file"]
            class_name = peripheral["class_name"]

            # Import peripheral library
            module_instance= __import__(module_name, fromlist=[class_name])
            class_instance = getattr(module_instance, class_name)

            # Create peripheral object instances
            self.peripheral[peripheral_name] = class_instance(peripheral_name, self.config["peripherals"][peripheral_name], self.env, self.sys)


    def spawn_peripherals(self):
        """ Runs peripheral threads. """
        for peripheral_name in self.peripheral:
            self.peripheral[peripheral_name].spawn()


    def all_peripherals_ready(self):
        """ Check that all peripherals are either in NOS, WARMING, or 
            ERROR states. """
        for peripheral in self.sys.peripheral_state:
            individual_peripheral = self.sys.peripheral_state[peripheral]
            if individual_peripheral["state"] != self.states.NOS and \
                individual_peripheral["state"] != self.states.WARMING and \
                individual_peripheral["state"] != self.states.ERROR:
                    self.logger.info("Waiting for peripherals to be ready")
                    return False
        return True


    def log_all(self):
        with threading.Lock():
            log = self.env.get_log()
            log += self.sys.get_log()
            self.logger.info(log)

