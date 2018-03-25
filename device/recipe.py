# Import python modules
import logging, time, threading, os

# Import all possible states & errors
from device.utility.states import States
from device.utility.errors import Errors

# Import db models from django
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()
from app.models import RecipeTransition


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

    # Initialize recipe file
    recipe = None


    def __init__(self, env, sys):
        """ Initializes recipe handler """
        self.env = env
        self.sys = sys

        # Set state & error values
        self.state = self.states.SETUP
        self.error = self.errors.NONE

        # Initialize thread object
        self.thread = None

        # Initialize recipe timing
        if "last_update_minute" not in self.sys.recipe_state:
            with threading.Lock():
                self.sys.recipe_state["last_update_minute"] = 0


    @property
    def state(self):
        """ Gets state value. """
        return self._state


    @state.setter
    def state(self, value):
        """ Safely updates recipe state in system object each time
            it is changed. """
        self._state = value
        with threading.Lock():
            self.sys.recipe_state["state"] = self._state


    def commanded_state(self):
        """ Gets the recipe's commanded state. """
        if "commanded_state" in self.sys.recipe_state:
            return self.sys.recipe_state["commanded_state"]
        else:
            return None


    @property
    def error(self):
        """ Gets error value. """
        return self._error


    @error.setter
    def error(self, value):
        """ Safely updates recipe error in system object each time
            it is changed. """
        self._error= value
        with threading.Lock():
            self.sys.recipe_state["error"] = self._error


    def spawn(self):
        """ Spawns recipe thread. """
        self.thread = threading.Thread(target=self.state_machine)
        self.thread.daemon = True
        self.thread.start()


    def state_machine(self):
        """ Runs state machine. """
        self.logger.debug("Starting state machine")
        while True:
            if self.state == self.states.SETUP:
                self.setup_state()
            elif self.state == self.states.START:
                self.start_state()
            elif self.state == self.states.RUN:
                self.run_state()
            elif self.state == self.states.PAUSE:
                self.pause_state()
            elif self.state == self.states.STOP:
                self.stop_state()
            elif self.state == self.states.ERROR:
                self.error_state()
            elif self.state == self.states.RESET:
                self.reset_state()


    def setup_state(self):
        """ Runs setup state. Loads stored recipe state and transitions 
            accordingly. """
        self.logger.info("Entered SETUP state")

        # TODO: Load stored state from system

        # Pretend we loaded in START state
        self._state = self.states.START

        # Wait for transition out of setup
        while self.state == self.states.SETUP:
            time.sleep(0.1)



    def start_state(self):
        """ Runs start state. Loads recipe dict into recipe transition table 
            in database. Updates recipe start timestamp in `system` shared 
            memory object. """
        self.logger.info("Entered START state")
        try:
            self.load_recipe_dict(self.sys.recipe_dict)
            with threading.Lock():
                self.sys.recipe_state["start_timestamp_minutes"] = self.timestamp_minutes()
            self.state = self.states.RUN
        except:
            self.logger.exception("Unable to load recipe dict.")
            self.state = self.states.ERROR
            self.error = self.errors.RECIPE_LOAD_ERROR


    def run_state(self):
        """ Runs run state. """
        self.logger.info("Entered RUN state")
        while True:
            current_minute = self.timestamp_minutes() - self.sys.recipe_state["start_timestamp_minutes"] 
            if current_minute > self.sys.recipe_state["last_update_minute"]:
                environment = self.get_recipe_environment_obj(current_minute)
                # TODO: only update state if new
                with threading.Lock():
                    self.sys.recipe_state["last_update_minute"] = current_minute
                    self.sys.recipe_state["phase"] = environment.phase
                    self.sys.recipe_state["cycle"] = environment.cycle
                    self.sys.recipe_state["environment_name"] = environment.environment_name
                    self.sys.recipe_state["environment_state"] = environment.environment_state
                    self.env.set_desired_sensor_values(environment.environment_state)

            # Check for transition to reset
            if self.commanded_state() == self.states.RESET:
                self.state = self.states.RESET
                continue

            # Update thread every 100ms
            time.sleep(0.1) 


    def pause_state(self):
        """ Runs pause state. """
        self.logger.info("Entered PAUSE state")


    def stop_state(self):
        """ Runs run state. """
        self.logger.info("Entered STOP state")


    def error_state(self):
        """ Runs error state. Waits for commanded state to be set to reset,
            then transitions to reset state. """
        self.logger.info("Entered ERROR state")

        # Update recipe state to reflect error state
        with threading.Lock():
            self.sys.recipe_state["last_update_minute"] = -1
            self.sys.recipe_state["phase"] = "Error"
            self.sys.recipe_state["cycle"] = 'Error'
            self.sys.recipe_state["environment_name"] = "Error"
            self.sys.recipe_state["environment_state"] = {}

        # TODO: How to update desired sensor values in error state?

        while (self.commanded_state() != self.states.RESET):
            time.sleep(0.1) # 100ms
        self.state = self.states.RESET


    def reset_state(self):
        """ Runs reset state. Resets device state then transitions to 
            initialization state. """
        self.logger.info("Entered RESET state")

        # Reset recipe state
        with threading.Lock():
            self.sys.recipe_state["last_update_minute"] = -1
            self.sys.recipe_state["phase"] = "Reset"
            self.sys.recipe_state["cycle"] = 'Reset'
            self.sys.recipe_state["environment_name"] = "Reset"
            self.sys.recipe_state["environment_state"] = {}

        # TODO: How to handle resetting desired sensor values?

        self.error = self.errors.NONE
        self.state = self.state.INIT


    def get_recipe_environment_obj(self, minute):
        """ Gets environment object from database for provided minute. Returns 
            most recent transition state. """
        return RecipeTransition.objects.filter(minute__lte=minute).order_by('-minute').first()


    def load_recipe_dict(self, recipe):
        """ Loads recipe file into database. Parses phased recipe into
            time-banded environment states"""

        # Clear parsed recipe table in database
        RecipeTransition.objects.all().delete()

        # Parse recipe file into database
        minute_counter = 0
        for phase in recipe["phases"]:
            phase_name = phase["name"]
            for i in range(phase["repeat"]):
                for cycle in phase["cycles"]:
                    # Get environment name and state + cycle name
                    environment_name = cycle["environment"]
                    environment_state = recipe["environments"][environment_name]
                    cycle_name = cycle["name"]

                    # Get duration
                    if "duration_hours" in cycle:
                        duration_hours = cycle["duration_hours"]
                        duration_minutes = duration_hours * 60
                    elif "duration_minutes" in cycle:
                        duration_minutes = cycle["duration_minutes"]
                    else:
                        raise KeyError("Could not find 'duration_minutes' or 'duration_hours' in cycle")

                    # Write time-banded environment states to the database
                    RecipeTransition.objects.create(
                        minute = minute_counter,
                        phase = phase_name,
                        cycle = cycle_name,
                        environment_name = environment_name,
                        environment_state = environment_state
                    )
                    minute_counter += duration_minutes

        # Set recipe end
        RecipeTransition.objects.create(
            minute = minute_counter,
            phase = "End",
            cycle = "End",
            environment_name = "End",
            environment_state = {}
        )


    def timestamp_minutes(self):
        """ Get timestamp in minutes. """
        return int(time.time() / 60)