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
    """ Recipe handler. Manages recipe state machine and interactions
        with recipe table in database. """

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
        self.nullify_recipe_state()

    @property
    def mode(self):
        """ Gets mode value. """
        return self._mode


    @mode.setter
    def mode(self, value):
        """ Safely updates recipe mode in device state. """
        self._mode = value
        with threading.Lock():
            self.state.recipe["mode"] = self._mode


    @property
    def error(self):
        """ Gets error value. """
        return self._error


    @error.setter
    def error(self, value):
        """ Safely updates recipe error in device state. """
        self._error= value
        with threading.Lock():
            self.state.recipe["error"] = self._error


    def commanded_mode(self):
        """ Gets the recipe's commanded mode. """
        if "commanded_mode" in self.state.recipe:
            return self.state.recipe["commanded_mode"]
        else:
            return None


    def commanded_recipe(self):
        """ Gets the recipe's commanded mode. """
        if "commanded_recipe" in self.state.recipe:
            return self.state.recipe["commanded_recipe"]
        else:
            return None


    def commanded_start_timestamp_minutes(self):
        """ Gets the recipe's commanded mode. """
        if "commanded_start_timestamp_minutes" in self.state.recipe:
            return self.state.recipe["commanded_start_timestamp_minutes"]
        else:
            return None


    def spawn(self):
        """ Spawns recipe thread. """
        self.thread = threading.Thread(target=self.run_state_machine)
        self.thread.daemon = True
        self.thread.start()


    def run_state_machine(self):
        """ Runs recipe state machine. """
        self.logger.debug("Starting recipe state machine")
        while True:
            if self.mode == Mode.INIT:
                self.run_init_mode()
            elif self.mode == Mode.LOAD:
                self.run_load_mode()
            elif self.mode == Mode.WAIT:
                self.run_wait_mode()        
            elif self.mode == Mode.NOM:
                self.run_nom_mode()
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


    def run_init_mode(self):
        """ Runs initialization mode. Waits for load command then 
            transitions to LOAD. """
        self.logger.info("Entered INIT")
        time.sleep(2)

        # Wait for load command
        while True:
            self.logger.info("mode: {}".format(self.mode))
            if self.commanded_mode() == Mode.LOAD:
                self.mode = self.commanded_mode()
                break
            time.sleep(0.5)


    def run_load_mode(self):
        """ Runs load mode. Nullifies recipe state and desired sensor state,
        loads recipe start time, if not set, starts recipe immediately, loads 
        recipe and start timestamp into device state, loads recipe transitions 
        into database, then transitions to WAIT. """
        self.logger.info("Entered LOAD")

        # Nullify recipe state and desired sensor state
        self.nullify_recipe_state()
        self.nullify_desired_sensor_state()

        # Load recipe start time, if not set, start recipe immediately
        if self.commanded_start_timestamp_minutes() != None:
            start_timestamp_minutes = commanded_start_timestamp_minutes()
        else:
            start_timestamp_minutes = self.timestamp_minutes()

        # Load recipe and start timestamp into device state and clear commanded states
        with threading.Lock(): 
            self.state.recipe["recipe"] = self.commanded_recipe()
            self.state.recipe["start_timestamp_minutes"] = start_timestamp_minutes
            self.state.recipe["commanded_recipe"] = None
            self.state.recipe["commanded_start_timestamp_minutes"] = None
            self.state.recipe["commanded_mode"] = None

        # Load recipe transitions into database
        self.load_recipe_transitions()

        # Transition to WAIT
        self.mode = Mode.WAIT


    def run_wait_mode(self):
        """ Runs wait mode. Waits for recipe start timestamp to be greater than
        or equal to current timestamp then transitions to NOM. """
        while True:
            if self.state.recipe["start_timestamp_minutes"] >= self.timestamp_minutes():
                self.mode = Mode.NOM
                break


    def run_nom_mode(self):
        """ Runs normal operation mode. Updates recipe and environment states 
        every minute. Transitions to PAUSE, RESET, or STOP if commanded. """

        self.logger.info("Entered NOM")
        self.update_recipe_environment()

        while True:
            # Update recipe and environment states every minute
            if self.new_minute():
                self.update_recipe_environment()

            # Check for transition to PAUSE
            if self.commanded_mode() == Mode.PAUSE:
                self.mode = Mode.PAUSE
                break

            # Check for transition to STOP
            if self.commanded_mode() == Mode.STOP:
                self.mode = Mode.STOP
                break
                
            # Check for transition to RESET
            if self.commanded_mode() == Mode.RESET:
                self.mode = Mode.RESET
                break

            # Update thread every 100ms
            time.sleep(0.1) 


    def run_pause_mode(self):
        """ Runs pause mode. """
        self.logger.info("Entered PAUSE")
        while True:
            time.sleep(0.1) # 100ms


    def run_resume_mode(self):
        """ Runs resume mode. """
        self.logger.info("Entered RESUME")
        while True:
            time.sleep(0.1) # 100ms


    def run_stop_mode(self):
        """ Runs stop mode. """
        self.logger.info("Entered STOP")


    def run_error_mode(self):
        """ Runs error mode. Nullifies recipe state and desired sensor state,
            waits for reset mode command then transitions to RESET. """
        self.logger.info("Entered ERROR")
        
        # Nullify recipe state and desired sensor state
        self.nullify_recipe_state()
        self.nullify_desired_sensor_state()

        # Wait for reset mode command
        while True:
            if self.commanded_mode() == Mode.RESET:
                self.mode == self.commanded_mode()
                break
            time.sleep(0.1) # 100ms

        # Transition to reset mode
        self.mode = Mode.RESET


    def run_reset_mode(self):
        """ Runs reset mode. Nullifies recipe state and desired sensor state,
            clears error, then transitions to INIT. """
        self.logger.info("Entered RESET")

        # Nullify recipe state and desired sensor state
        self.nullify_recipe_state()
        self.nullify_desired_sensor_state()

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


    def update_recipe_environment(self):
        """ Updates recipe environment. """
        current_minute = self.timestamp_minutes() - self.state.recipe["start_timestamp_minutes"]
        environment = self.get_recipe_environment(current_minute)
    
        self.update_recipe_state(
            phase=environment.phase, 
            cycle=environment.cycle, 
            env_name=environment.environment_name, 
            env_state=environment.environment_state, 
            last_update_min=current_minute)


    def nullify_desired_sensor_state(self):
        """ Sets desired sensor state to null values. """
        with threading.Lock():
            for variable in self.state.environment["sensor"]["desired"]:
                self.state.environment["sensor"]["desired"][variable] = None


    def nullify_recipe_state(self):
        """ Sets recipe state to null values """
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
                self.state.recipe["name"] = name
            if phase is not None:
                self.state.recipe["phase"] = phase
            if cycle is not None:
                self.state.recipe["cycle"] = cycle
            if env_name is not None:
                self.state.recipe["environment_name"] = env_name
            if env_state is not None:
                self.state.recipe["environment_state"] = env_state
                for variable in env_state:
                    self.set_desired_sensor_values(env_state)
            if last_update_min is not None:
                self.state.recipe["last_update_minute"] = last_update_min
                if last_update_min == -1:
                    self.state.recipe["percent_complete"] = None
                    self.state.recipe["percent_complete_string"] = None
                    self.state.recipe["time_remaining_minutes"] = None
                    self.state.recipe["time_remaining_string"] = None
                    self.state.recipe["time_elapsed_string"] = None
                else:
                    # Update duration minutes
                    duration_min = self.state.recipe["duration_minutes"]

                    # Update percent complete
                    percent_complete = float(last_update_min) / duration_min * 100
                    self.state.recipe["percent_complete"] = percent_complete
                    
                    # Update percent complete string
                    percent_complete_string = "{0:.2f}".format(percent_complete)
                    self.state.recipe["percent_complete_string"] = percent_complete_string
                    
                    # Update time remaining minutes
                    time_remaining_minutes = duration_min - last_update_min
                    self.state.recipe["time_remaining_minutes"] = time_remaining_minutes
                    
                    # Update time remaining string
                    time_remaining_string = self.get_duration_string(time_remaining_minutes)
                    self.state.recipe["time_remaining_string"] = time_remaining_string

                    # Update time elapsed string
                    time_elapsed_string = self.get_duration_string(last_update_min)
                    self.state.recipe["time_elapsed_string"] = time_elapsed_string

            if start_timestamp_min is not None:
                self.state.recipe["start_timestamp_minutes"] = start_timestamp_min
                started = datetime.datetime.fromtimestamp(start_timestamp_min*60).strftime('%Y-%m-%d %H:%M:%S') + " UTC"
                self.state.recipe["start_datestring"] = started
            if duration_min is not None:
                self.state.recipe["duration_minutes"] = duration_min
                if duration_min == -1:
                    self.state.recipe["duration_string"] = None 
                else:
                    self.state.recipe["duration_string"] = self.get_duration_string(duration_min)


    def new_minute(self):
        """ Check if system clock is on a new minute. """
        current_minute = self.timestamp_minutes() - self.state.recipe["start_timestamp_minutes"] 
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
