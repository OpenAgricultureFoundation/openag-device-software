# Import python modules
import logging, time, threading, os, datetime, json

# Import device modes and errors
from device.utility.mode import Mode
from device.utility.error import Error

# Import database models
import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()
from app.models import RecipeTransition


class Recipe:
    """ Manages recipe state machine. """

    # Initialize logger
    logger = logging.getLogger(__name__)

    # Initialize mode & error variables
    _mode = None
    _error = None


    # Initialize thread object
    thread = None


    def __init__(self, state):
        """ Initializes recipe handler """
        self.state = state
        self.mode = Mode.INIT
        self.error = Error.NONE

    @property
    def mode(self):
        """ Gets mode value. """
        return self._mode


    @mode.setter
    def mode(self, value):
        """ Safely updates recipe mode in shared state. """
        self._mode = value
        with threading.Lock():
            self.state.recipe["mode"] = value


    @property
    def commanded_mode(self):
        """ Gets the recipe's commanded mode. """
        if "commanded_mode" in self.state.recipe:
            return self.state.recipe["commanded_mode"]
        else:
            return None

    @commanded_mode.setter
    def commanded_mode(self, value):
        """ Safely updates commanded mode in shared state. """
        with threading.Lock():
            self.state.recipe["commanded_mode"] = value


    @property
    def recipe(self):
        """ Gets the recipe's recipe mode. """
        if "recipe" in self.state.recipe:
            return self.state.recipe["recipe"]
        else:
            return None


    @recipe.setter
    def recipe(self, value):
        """ Safely updates recipe in shared state. """
        with threading.Lock():
            self.state.recipe["recipe"] = value


    @property
    def commanded_recipe(self):
        """ Gets the recipe's commanded mode. """
        if "commanded_recipe" in self.state.recipe:
            return self.state.recipe["commanded_recipe"]
        else:
            return None


    @commanded_recipe.setter
    def commanded_recipe(self, value):
        """ Safely updates commanded recipe in shared state. """
        with threading.Lock():
            self.state.recipe["commanded_recipe"] = value


    @property
    def error(self):
        """ Gets error value. """
        return self._error


    @error.setter
    def error(self, value):
        """ Safely updates recipe error in shared state. """
        self._error= value
        with threading.Lock():
            self.state.recipe["error"] = value


    @property
    def current_timestamp_minutes(self):
        """ Get current timestamp in minutes. """
        return int(time.time() / 60)


    @property
    def start_timestamp_minutes(self):
        """ Gets start timestamp minutes from shared state. """
        if "start_timestamp_minutes" in self.state.recipe:
            return self.state.recipe["start_timestamp_minutes"]
        else:
            return None


    @start_timestamp_minutes.setter
    def start_timestamp_minutes(self, value):
        """ Generates start datestring then safely updates start timestamp 
            minutes and datestring in shared state. """

        # Generate start datestring
        if value != None:
            start_datestring = datetime.datetime.fromtimestamp(value*60).\
                strftime('%Y-%m-%d %H:%M:%S') + " UTC"
        else:
            start_datestring = None

        # Update start timestamp minutes and datestring in shared state
        with threading.Lock():
            self.state.recipe["start_timestamp_minutes"] = value
            self.state.recipe["start_datestring"] = start_datestring


    @property
    def commanded_start_timestamp_minutes(self):
        """ Gets the recipe's commanded mode from shared state. """
        if "commanded_start_timestamp_minutes" in self.state.recipe:
            return self.state.recipe["commanded_start_timestamp_minutes"]
        else:
            return None


    @commanded_start_timestamp_minutes.setter
    def commanded_start_timestamp_minutes(self, value):
        """ Safely updates commanded_start_timestamp_minutes 
            in shared state. """
        with threading.Lock():
            self.state.recipe["commanded_start_timestamp_minutes"] = value


    @property
    def start_datestring(self):
        """ Gets start datestring value from shared state. """
        if "start_datestring" in self.state.recipe:
            return self.state.recipe["start_datestring"]
        else:
            return None


    @property
    def duration_minutes(self):
        """ Gets recipe duration in minutes from shared state. """
        if "duration_minutes" in self.state.recipe:
            return self.state.recipe["duration_minutes"]
        else:
            return None


    @duration_minutes.setter
    def duration_minutes(self, value):
        """ Generates duration string then safely updates duration string 
            and minutes in shared state. """

        # Generate duation string
        if value != None:
            duration_string = self.get_duration_string(value)
        else:
            duration_string = None

        # Safely update duration minutes and string in shared state
        with threading.Lock():
            self.state.recipe["duration_minutes"] = value
            self.state.recipe["duration_string"] = duration_string


    @property
    def last_update_minute(self):
        """ Gets the last update minute from shared state. """
        if "last_update_minute" in self.state.recipe:
            return self.state.recipe["last_update_minute"]
        else:
            return None


    @last_update_minute.setter
    def last_update_minute(self, value):
        """ Generates percent complete, percent complete string, time
            remaining minutes, time remaining string, and time elapsed
            string then safely updates last update minute and aforementioned
            values in shared state. """
        
        # Generate values
        if value != None:
            percent_complete = float(value) / self.duration_minutes * 100
            percent_complete_string = "{0:.2f}".format(percent_complete)
            time_remaining_minutes = self.duration_minutes - value
            time_remaining_string = self.get_duration_string(time_remaining_minutes)
            time_elapsed_string = self.get_duration_string(value)
        else:
            percent_complete = None
            percent_complete_string = None
            time_remaining_minutes = None
            time_remaining_string = None
            time_elapsed_string = None

        # Safely update values in shared state
        with threading.Lock():
            self.state.recipe["last_update_minute"] = value
            self.state.recipe["percent_complete"] = percent_complete
            self.state.recipe["percent_complete_string"] = percent_complete_string
            self.state.recipe["time_remaining_minutes"] = time_remaining_minutes
            self.state.recipe["time_remaining_string"] = time_remaining_string
            self.state.recipe["time_elapsed_string"] = time_elapsed_string


    @property
    def percent_complete(self):
        """ Gets percent complete from shared state. """
        if "percent_complete" in self.state.recipe:
            return self.state.recipe["percent_complete"]
        else:
            return None

    @property
    def percent_complete_string(self):
        """ Gets percent complete string from shared state. """
        if "percent_complete_string" in self.state.recipe:
            return self.state.recipe["percent_complete_string"]
        else:
            return None

    @property
    def time_remaining_minutes(self):
        """ Gets time remaining minutes from shared state. """
        if "time_remaining_minutes" in self.state.recipe:
            return self.state.recipe["time_remaining_minutes"]
        else:
            return None

    @property
    def time_remaining_string(self):
        """ Gets time remaining string from shared state. """
        if "time_remaining_string" in self.state.recipe:
            return self.state.recipe["time_remaining_string"]
        else:
            return None

    @property
    def time_elapsed_string(self):
        """ Gets time elapsed string from shared state. """
        if "time_elapsed_string" in self.state.recipe:
            return self.state.recipe["time_elapsed_string"]
        else:
            return None


    @property
    def current_phase(self):
        """ Gets the recipe current phase from shared state. """
        if "current_phase" in self.state.recipe:
            return self.state.recipe["current_phase"]
        else:
            return None


    @current_phase.setter
    def current_phase(self, value):
        """ Safely updates current phase in shared state. """
        with threading.Lock():
            self.state.recipe["current_phase"] = value


    @property
    def current_cycle(self):
        """ Gets the current cycle from shared state. """
        if "current_cycle" in self.state.recipe:
            return self.state.recipe["current_cycle"]
        else:
            return None


    @current_cycle.setter
    def current_cycle(self, value):
        """ Safely updates current cycle in shared state. """
        with threading.Lock():
            self.state.recipe["current_cycle"] = value


    @property
    def current_environment_name(self):
        """ Gets the current environment name from shared state. """
        if "current_environment_name" in self.state.recipe:
            return self.state.recipe["current_environment_name"]
        else:
            return None


    @current_environment_name.setter
    def current_environment_name(self, value):
        """ Safely updates current environment name in shared state. """
        with threading.Lock():
            self.state.recipe["current_environment_name"] = value


    @property
    def current_environment_state(self):
        """ Gets the current environment state from shared state. """
        if "current_environment_state" in self.state.recipe:
            return self.state.recipe["current_environment_state"]
        else:
            return None


    @current_environment_state.setter
    def current_environment_state(self, value):
        """ Safely updates current environment state in shared state. """
        with threading.Lock():
            self.state.recipe["current_environment_state"] = value
            self.set_desired_sensor_values(value)


    ######################## End of Getters / Setters #########################


    def spawn(self):
        """ Spawns recipe thread. """
        self.thread = threading.Thread(target=self.run_state_machine)
        self.thread.daemon = True
        self.thread.start()


    def run_state_machine(self):
        """ Runs recipe state machine. """
        while True:
            if self.mode == Mode.INIT:
                self.run_init_mode()
            if self.mode == Mode.NORECIPE:
                self.run_norecipe_mode()  
            elif self.mode == Mode.LOAD:
                self.run_load_mode()
            elif self.mode == Mode.QUEUED:
                self.run_queued_mode()        
            elif self.mode == Mode.NORMAL:
                self.run_normal_mode()
            elif self.mode == Mode.PAUSE:
                self.run_pause_mode()
            elif self.mode == Mode.RESUME:
                self.run_resume_mode()
            elif self.mode == Mode.STOP:
                self.run_stop_mode()
            elif self.mode == Mode.ERROR:
                self.run_error_mode()
            elif self.mode == Mode.RESET:
                self.run_reset_mode()
            else:
                self.error = Error.INVALID_MODE
                self.logger.critial("Invalid state machine mode")
                time.sleep(0.1)


    def run_init_mode(self):
        """ Runs initialization mode. Transitions to stored recipe mode 
            or NORECIPE if no stored mode. """
        self.error = Error.NONE
        # self.clear_recipe_state()

        # Transition to recipe stored mode
        if "stored_mode" in self.state.recipe and \
            self.state.recipe["stored_mode"] != None:
            self.mode = self.state.recipe["stored_mode"]
        else:
            self.mode = Mode.NORECIPE


    def run_norecipe_mode(self):
        """ Runs no recipe mode. Waits for load command then 
            transitions to LOAD. """
        self.logger.info("Entered NORECIPE")

        self.clear_recipe_state()

        # Wait for load command
        while True:
            if self.commanded_mode == Mode.LOAD:
                self.mode = self.commanded_mode
                break
            time.sleep(0.1) # 100ms


    def run_load_mode(self):
        """ Runs load mode. Loads recipe transitions into database, loads 
            recipe start time, signals start of experiment, then 
            transitions to QUEUED. """
        self.logger.info("Entered LOAD")

        # Load recipe into shared state
        self.recipe = self.commanded_recipe

        # Load recipe transitions into database
        self.load_recipe_transitions()

        # Load recipe start time, if not set, start recipe immediately
        if self.commanded_start_timestamp_minutes != None:
            self.start_timestamp_minutes = commanded_start_timestamp_minutes
        else:
            self.start_timestamp_minutes = self.current_timestamp_minutes

        # Clear commanded states
        self.commanded_mode = None
        self.commanded_recipe = None
        self.commanded_start_timestamp_minutes = None

        # Transition to QUEUED
        self.mode = Mode.QUEUED


    def run_queued_mode(self):
        """ Runs queued mode. Waits for recipe start timestamp to be greater than
        or equal to current timestamp then transitions to NORMAL. """
        while True:
            if self.start_timestamp_minutes >= self.current_timestamp_minutes:
                self.mode = Mode.NORMAL
                break


    def run_normal_mode(self):
        """ Runs normal operation mode. Updates recipe and environment states 
        every minute. Transitions to PAUSE or STOP if commanded. """

        self.logger.info("Entered NORMAL")
        self.update_recipe_environment()

        while True:
            # Update recipe and environment states every minute
            if self.new_minute():
                self.update_recipe_environment()

            # Check for transition to PAUSE
            if self.commanded_mode == Mode.PAUSE:
                self.mode = Mode.PAUSE
                break

            # Check for transition to STOP
            if self.commanded_mode == Mode.STOP:
                self.mode = Mode.STOP
                break

            # Update thread every 100ms
            time.sleep(0.1) 


    def run_pause_mode(self):
        """ Runs pause mode. Clears recipe and desired sensor state, waits 
            for resume or stop command"""
        self.logger.info("Entered PAUSE")

        # Clear recipe and desired sensor state
        self.clear_recipe_state()
        self.clear_desired_sensor_state()

        while True:
            # Check for transition to NORMAL
            if self.commanded_mode == Mode.NORMAL:
                self.mode = Mode.NORMAL
                break

            # Check for transition to STOP
            if self.commanded_mode == Mode.STOP:
                self.mode = Mode.STOP
                break

            # Update every 100ms
            time.sleep(0.1) # 100ms


    def run_stop_mode(self):
        """ Runs stop mode. Clears recipe and desired sensor state, signals 
            end of recipe, then transitions to NORECIPE. """
        self.logger.info("Entered STOP")

        # Clear recipe and desired sensor states
        self.clear_recipe_state()
        self.clear_desired_sensor_state()

        # Transition to NORECIPE
        self.mode = NORECIPE


    def run_error_mode(self):
        """ Runs error mode. Clears recipe state and desired sensor state,
            waits for reset mode command then transitions to RESET. """
        self.logger.info("Entered ERROR")
        
        # Nullify recipe state and desired sensor state
        self.clear_recipe_state()
        self.clear_desired_sensor_state()

        # Wait for reset mode command
        while True:
            if self.commanded_mode == Mode.RESET:
                self.mode == self.commanded_mode
                break
            time.sleep(0.1) # 100ms

        # Transition to reset mode
        self.mode = Mode.RESET


    def run_reset_mode(self):
        """ Runs reset mode. Clears error state then transitions to INIT. """
        self.logger.info("Entered RESET")

        # Clear error
        self.error = Error.NONE

        # Transition to INIT
        self.mode = Mode.INIT


    def get_recipe_environment(self, minute):
        """ Gets environment object from database for provided minute. """
        return RecipeTransition.objects.filter(minute__lte=minute).order_by('-minute').first()


    def load_recipe_transitions(self):
        """ Loads recipe transitions into database. """

        # Clear recipe transition table in database
        RecipeTransition.objects.all().delete()

        # Parse recipe into database
        minute_counter = 0
        for phase in self.state.recipe["recipe"]["phases"]:
            phase_name = phase["name"]
            for i in range(phase["repeat"]):
                for cycle in phase["cycles"]:
                    # Get environment name and state + cycle name
                    environment_name = cycle["environment"]
                    environment_state = self.state.recipe["recipe"]["environments"][environment_name]
                    cycle_name = cycle["name"]

                    # Get duration
                    if "duration_hours" in cycle:
                        duration_hours = cycle["duration_hours"]
                        duration_minutes = duration_hours * 60
                    elif "duration_minutes" in cycle:
                        duration_minutes = cycle["duration_minutes"]
                    else:
                        raise KeyError("Could not find 'duration_minutes' or 'duration_hours' in cycle")

                    # Write recipe transition to database
                    RecipeTransition.objects.create(
                        minute = minute_counter,
                        phase = phase_name,
                        cycle = cycle_name,
                        environment_name = environment_name,
                        environment_state = environment_state
                    )
                    minute_counter += duration_minutes

                    # Update duration minutes
                    self.duration_minutes = minute_counter


        # Set recipe end
        RecipeTransition.objects.create(
            minute = minute_counter,
            phase = "End",
            cycle = "End",
            environment_name = "End",
            environment_state = {}
        )


    def update_recipe_environment(self):
        """ Updates recipe environment. """
        self.last_update_minute = self.current_timestamp_minutes - self.start_timestamp_minutes
        environment = self.get_recipe_environment(self.last_update_minute)

        self.current_phase = environment.phase
        self.current_cycle = environment.cycle
        self.current_environment_name = environment.environment_name
        self.current_environment_state = environment.environment_state


    def clear_desired_sensor_state(self):
        """ Sets desired sensor state to null values. """
        with threading.Lock():
            for variable in self.state.environment["sensor"]["desired"]:
                self.state.environment["sensor"]["desired"][variable] = None


    def clear_recipe_state(self):
        """ Sets recipe state to null values """
        self.duration_minutes = None
        self.last_update_min = None
        self.current_phase = None
        self.current_cycle = None
        self.current_environment_name = None
        self.current_environment_state = {}


    def new_minute(self):
        """ Check if system clock is on a new minute. """
        current_minute = self.current_timestamp_minutes - self.start_timestamp_minutes
        last_update_minute = self.state.recipe["last_update_minute"]
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


    def set_desired_sensor_values(self, environment_dict):
        """ Sets desired sensor values from provided environment dict. """
        with threading.Lock():
            for variable in environment_dict:
                self.state.environment["sensor"]["desired"][variable] = environment_dict[variable]