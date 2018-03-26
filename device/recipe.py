# Import python modules
import logging, time, threading, os, datetime, json

# Import all possible states & errors
from device.utility.states import States
from device.utility.errors import Errors

# Import database models
import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()
from app.models import RecipeTransition
from app.models import Device as DeviceModel


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

        # Initialize recipe state
        self.set_null_recipe_state()

        # Load stored state 
        self.load_stored_recipe_state()

        # Pretend we loaded in START state
        # self._state = self.states.START

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
            self.state = self.states.RUN
        except:
            self.logger.exception("Unable to load recipe dict.")
            self.state = self.states.ERROR
            self.error = self.errors.RECIPE_LOAD_ERROR


    def run_state(self):
        """ Runs run state. """
        self.logger.info("Entered RUN state")
        self.update_recipe_environment()

        while True:
            # Update recipe environment every minute
            if self.new_minute():
                self.update_recipe_environment()
                
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
        self.set_null_recipe_state()

        # TODO: How to update desired sensor values in error state?

        while (self.commanded_state() != self.states.RESET):
            time.sleep(0.1) # 100ms
        self.state = self.states.RESET


    def reset_state(self):
        """ Runs reset state. Resets device state then transitions to 
            initialization state. """
        self.logger.info("Entered RESET state")
        self.set_null_recipe_state()

        # TODO: How to handle resetting desired sensor values?

        self.error = self.errors.NONE
        self.state = self.state.INIT


    def get_recipe_environment_obj(self, minute):
        """ Gets environment object from database for provided minute. Returns 
            most recent transition state. """
        return RecipeTransition.objects.filter(minute__lte=minute).order_by('-minute').first()


    def load_stored_recipe_state(self):
        """ Load recipe state stored in database. """
        dev = DeviceModel.objects.filter(pk=1).first()
        with threading.Lock():
            self.sys.recipe_state = json.loads(dev.recipe_state)


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

        # Update recipe state
        self.update_recipe_state(
            name=recipe["name"],
            duration_min = minute_counter,
            start_timestamp_min=self.timestamp_minutes())


    def timestamp_minutes(self):
        """ Get timestamp in minutes. """
        return int(time.time() / 60)


    def update_recipe_environment(self):
        """ Updates recipe environment. """
        current_minute = self.timestamp_minutes() - self.sys.recipe_state["start_timestamp_minutes"]
        environment = self.get_recipe_environment_obj(current_minute)
    
        self.update_recipe_state(
            phase=environment.phase, 
            cycle=environment.cycle, 
            env_name=environment.environment_name, 
            env_state=environment.environment_state, 
            last_update_min=current_minute)


    def set_null_recipe_state(self):
        """ Clears recipe state. """
        self.update_recipe_state(
            name=None, 
            phase=None, 
            cycle=None, 
            env_name=None,
            env_state={}, 
            last_update_min=-1, 
            duration_min=-1)


    def update_recipe_state(self, name=None, phase=None, cycle=None, 
        env_name=None, env_state=None, last_update_min=None, 
        start_timestamp_min=None, duration_min=None):
        """ Safely update recipe state with provided parameters. """

        with threading.Lock():
            if name is not None:
                self.sys.recipe_state["name"] = name
            if phase is not None:
                self.sys.recipe_state["phase"] = phase
            if cycle is not None:
                self.sys.recipe_state["cycle"] = cycle
            if env_name is not None:
                self.sys.recipe_state["environment_name"] = env_name
            if env_state is not None:
                self.sys.recipe_state["environment_state"] = env_state
                for variable in env_state:
                    self.env.set_desired_sensor_values(env_state)
            if last_update_min is not None:
                self.sys.recipe_state["last_update_minute"] = last_update_min
                if last_update_min == -1:
                    self.sys.recipe_state["percent_complete"] = None
                    self.sys.recipe_state["percent_complete_string"] = None
                    self.sys.recipe_state["time_remaining_minutes"] = None
                    self.sys.recipe_state["time_remaining_string"] = None
                    self.sys.recipe_state["time_elapsed_string"] = None

                else:
                    # Update duration minutes
                    duration_min = self.sys.recipe_state["duration_minutes"]

                    # Update percent complete
                    percent_complete = float(last_update_min) / duration_min * 100
                    self.sys.recipe_state["percent_complete"] = percent_complete
                    
                    # Update percent complete string
                    percent_complete_string = "{0:.2f}".format(percent_complete)
                    self.sys.recipe_state["percent_complete_string"] = percent_complete_string
                    
                    # Update time remaining minutes
                    time_remaining_minutes = duration_min - last_update_min
                    self.sys.recipe_state["time_remaining_minutes"] = time_remaining_minutes
                    
                    # Update time remaining string
                    time_remaining_string = self.get_duration_string(time_remaining_minutes)
                    self.sys.recipe_state["time_remaining_string"] = time_remaining_string

                    # Update time elapsed string
                    time_elapsed_string = self.get_duration_string(last_update_min)
                    self.sys.recipe_state["time_elapsed_string"] = time_elapsed_string


            if start_timestamp_min is not None:
                self.sys.recipe_state["start_timestamp_minutes"] = start_timestamp_min
                started = datetime.datetime.fromtimestamp(start_timestamp_min*60).strftime('%Y-%m-%d %H:%M:%S') + " UTC"
                self.sys.recipe_state["start_datestring"] = started
            if duration_min is not None:
                self.sys.recipe_state["duration_minutes"] = duration_min
                if duration_min == -1:
                    self.sys.recipe_state["duration_string"] = None 
                else:
                    self.sys.recipe_state["duration_string"] = self.get_duration_string(duration_min)


    def new_minute(self):
        """ Check if system clock is on a new minute. """
        current_minute = self.timestamp_minutes() - self.sys.recipe_state["start_timestamp_minutes"] 
        last_update_minute = self.sys.recipe_state["last_update_minute"]
        if current_minute > last_update_minute:
            return True
        else:
            return False


    def get_duration_string(self, duration_minutes):
        """ Converts duration in minutes to duration day-hour-minute string. """
        days = int(float(duration_minutes) / (60*24))
        hours = int((float(duration_minutes) - days*60*24) / 60)
        minutes = duration_minutes - days*60*24 - hours*60
        string = "{} Days {} Hours {} Minutes".format(days, hours, minutes)
        return string


