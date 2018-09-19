# Import python modules
import logging, time, threading, os, sys, datetime, json

# Import device utilities
from device.utilities.modes import Modes

# Import device parsers
from device.recipe.parser import RecipeParser

# Import database models
from app.models import RecipeModel
from app.models import RecipeTransitionModel

# Import recipe modules
from device.recipe.events import RecipeEvents


class RecipeManager(RecipeEvents):
    """Manages recipe state machine thread."""

    # Define valid transition table
    transitions = {
        Modes.NORECIPE: [Modes.START],
        Modes.START: [Modes.QUEUED],
        Modes.QUEUED: [Modes.NORMAL, Modes.STOP],
        Modes.NORMAL: [Modes.PAUSE, Modes.STOP],
        Modes.PAUSE: [Modes.START],
        Modes.STOP: [Modes.NORECIPE],
        Modes.ERROR: [Modes.RESET],
    }

    # Initialize logger
    extra = {"console_name": "Recipe", "file_name": "Recipe"}
    logger = logging.getLogger("recipe")
    logger = logging.LoggerAdapter(logger, extra)

    # Initialize mode & error variables
    _mode = None

    # Initialize thread object
    thread = None

    def __init__(self, state):
        """Initializes recipe manager."""
        self.state = state
        self.mode = Modes.INIT
        self.stop_event = threading.Event()  # so we can stop this thread

    @property
    def mode(self):
        """Gets mode value. Important to keep this local so all
        state transitions only occur from within thread."""
        return self._mode

    @mode.setter
    def mode(self, value):
        """ Safely updates recipe mode in shared state. """
        self._mode = value
        with self.state.lock:
            self.state.recipe["mode"] = value

    @property
    def stored_mode(self):
        """ Gets the stored mode from shared state. """
        if "stored_mode" in self.state.recipe:
            return self.state.recipe["stored_mode"]
        else:
            return None

    @stored_mode.setter
    def stored_mode(self, value):
        """ Safely updates stored mode in shared state. """
        with self.state.lock:
            self.state.recipe["stored_mode"] = value

    @property
    def recipe_uuid(self):
        """ Gets recipe uuid from shared state. """
        if "recipe_uuid" in self.state.recipe:
            return self.state.recipe["recipe_uuid"]
        else:
            return None

    @recipe_uuid.setter
    def recipe_uuid(self, value):
        """ Safely updates recipe uuid in shared state. """
        with self.state.lock:
            self.state.recipe["recipe_uuid"] = value

    @property
    def recipe_name(self):
        """ Gets recipe name from shared state. """
        if "recipe_name" in self.state.recipe:
            return self.state.recipe["recipe_name"]
        else:
            return None

    @recipe_name.setter
    def recipe_name(self, value):
        """ Safely updates recipe name in shared state. """
        with self.state.lock:
            self.state.recipe["recipe_name"] = value

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
            start_datestring = (
                datetime.datetime.fromtimestamp(value * 60).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                + " UTC"
            )
        else:
            start_datestring = None

        # Update start timestamp minutes and datestring in shared state
        with self.state.lock:
            self.state.recipe["start_timestamp_minutes"] = value
            self.state.recipe["start_datestring"] = start_datestring

    @property
    def start_datestring(self):
        """Gets start datestring value from shared state."""
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
        with self.state.lock:
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
        if value != None and self.duration_minutes != None:
            percent_complete = float(value) / self.duration_minutes * 100
            percent_complete_string = "{0:.2f} %".format(percent_complete)
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
        with self.state.lock:
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
        with self.state.lock:
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
        with self.state.lock:
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
        with self.state.lock:
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
        with self.state.lock:
            self.state.recipe["current_environment_state"] = value
            self.set_desired_sensor_values(value)

    def spawn(self):
        """ Spawns recipe thread. """
        self.thread = threading.Thread(target=self.run_state_machine)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.stop_event.set()

    def stopped(self):
        return self.stop_event.is_set()

    def run_state_machine(self) -> None:
        """Runs recipe state machine."""
        while True:

            # Check for thread stop event..
            # TODO: this shouldnt be here...
            if self.stopped():
                break

            # Check for mode transitions
            if self.mode == Modes.INIT:
                self.run_init_mode()
            if self.mode == Modes.NORECIPE:
                self.run_norecipe_mode()
            elif self.mode == Modes.START:
                self.run_start_mode()
            elif self.mode == Modes.QUEUED:
                self.run_queued_mode()
            elif self.mode == Modes.NORMAL:
                self.run_normal_mode()
            elif self.mode == Modes.PAUSE:
                self.run_pause_mode()
            elif self.mode == Modes.RESUME:
                self.run_resume_mode()
            elif self.mode == Modes.STOP:
                self.run_stop_mode()
            elif self.mode == Modes.ERROR:
                self.run_error_mode()
            elif self.mode == Modes.RESET:
                self.run_reset_mode()
            else:
                self.logger.critial("Invalid state machine mode")
                time.sleep(0.1)

    def run_init_mode(self) -> None:
        """Runs initialization mode. Transitions to stored recipe mode or NORECIPE if 
        no stored mode."""
        self.logger.info("Entered INIT")

        # Check for stored mode
        mode = self.state.recipe.get("stored_mode")
        if mode != None:
            self.logger.debug("Returning to stored mode: {}".format(mode))
            self.mode = mode
        else:
            self.mode = Modes.NORECIPE

    def run_norecipe_mode(self):
        """Runs no recipe mode. Waits for start command then transitions to START."""
        self.logger.info("Entered NORECIPE")

        # Clear state
        self.clear_recipe_state()
        self.clear_desired_sensor_state()

        # Loop forever
        while True:

            # Check for events
            self.check_events()

            # Check for transitions
            if self.mode != Modes.NORECIPE:
                break

            # Update every 100ms
            time.sleep(0.1)

    def run_start_mode(self):
        """Runs start mode. Loads commanded recipe uuid into shared state, 
        retrieves recipe json from recipe table, generates recipe 
        transitions, stores them in the recipe transition table, extracts
        recipe duration and start time then transitions to QUEUED."""

        try:
            self.logger.info("Entered START")

            # Get recipe json from recipe uuid
            recipe_json = RecipeModel.objects.get(pk=self.recipe_uuid).json
            recipe_dict = json.loads(recipe_json)

            # Parse recipe transitions
            recipe_parser = RecipeParser()
            transitions = recipe_parser.parse(recipe_dict)

            # Store recipe transitions in database
            self.store_recipe_transitions(transitions)

            # Set recipe duration
            self.duration_minutes = transitions[-1]["minute"]

            # Set recipe name
            self.recipe_name = recipe_dict["name"]
            self.logger.info("Started: {}".format(self.recipe_name))

            # Transition to QUEUED
            self.mode = Modes.QUEUED
        except Exception as e:
            message = "Unable to start recipe, unhandled exception {}".format(e)
            self.logger.critical(message)
            self.mode = Modes.NORECIPE

    def run_queued_mode(self):
        """Runs queued mode. Waits for recipe start timestamp to be greater than
        or equal to current timestamp then transitions to NORMAL."""
        self.logger.info("Entered QUEUED")

        # Initialize time counter
        prev_time_seconds = 0

        # Loop forever
        while True:

            # Check if recipe is ready to run
            if self.current_timestamp_minutes >= self.start_timestamp_minutes:
                self.mode = Modes.NORMAL
                break

            # Calculate remaining delay time
            delay_minutes = self.start_timestamp_minutes - self.current_timestamp_minutes

            # Log remaining delay time every hour if remaining time > 1 hour
            if delay_minutes > 60 and time.time() > prev_time_seconds + 3600:
                prev_time_seconds = time.time()
                delay_hours = int(delay_minutes / 60.0)
                self.logger.debug("Starting recipe in {} hours".format(delay_hours))

            # Log remaining delay time every minute if remaining time < 1 hour
            elif delay_minutes < 60 and time.time() > prev_time_seconds + 60:
                prev_time_seconds = time.time()
                self.logger.debug("Starting recipe in {} minutes".format(delay_minutes))

            # Check for events
            self.check_events()

            # Check for transitions
            if self.mode != Modes.QUEUED:
                break

            # Update every 100ms
            time.sleep(0.1)

    def run_normal_mode(self):
        """ Runs normal operation mode. Updates recipe and environment states 
        every minute. Transitions to PAUSE or STOP if commanded. """
        self.logger.info("Entered NORMAL")

        # Update recipe environment on first entry
        self.update_recipe_environment()

        # Loop forever
        while True:

            # Update recipe and environment states every minute
            if self.new_minute():
                self.update_recipe_environment()

            # Check for recipe end
            if self.current_phase == "End" and self.current_cycle == "End":
                self.logger.info("Recipe is over, so transition from NORMAL to STOP")
                self.mode = Modes.STOP
                break

            # Check for events
            self.check_events()

            # Check for transitions
            if self.mode != Modes.NORMAL:
                break

            # Update every 100ms
            time.sleep(0.1)

    def run_pause_mode(self):
        """Runs pause mode. Clears recipe and desired sensor state, waits 
        for resume or stop command."""
        self.logger.info("Entered PAUSE")

        # Clear recipe and desired sensor state
        self.clear_recipe_state()
        self.clear_desired_sensor_state()

        # Loop forever
        while True:

            # Check for events
            self.check_events()

            # Check for transitions
            if self.mode != Modes.PAUSE:
                break

            # Update every 100ms
            time.sleep(0.1)

    def run_stop_mode(self):
        """Runs stop mode. Clears recipe and desired sensor state, signals 
        end of recipe, then transitions to NORECIPE."""
        self.logger.info("Entered STOP")

        # Clear recipe and desired sensor states
        self.clear_recipe_state()
        self.clear_desired_sensor_state()

        # Transition to NORECIPE
        self.mode = Modes.NORECIPE

    def run_error_mode(self):
        """Runs error mode. Clears recipe state and desired sensor state,
        waits for reset mode command then transitions to RESET."""
        self.logger.info("Entered ERROR")

        # Clear recipe and desired sensor states
        self.clear_recipe_state()
        self.clear_desired_sensor_state()

        # Loop forever
        while True:

            # Check for events
            self.check_events()

            # Check for transitions
            if self.mode != Modes.ERROR:
                break

            # Update every 100ms
            time.sleep(0.1)

    def run_reset_mode(self):
        """Runs reset mode. Clears error state then transitions to INIT."""
        self.logger.info("Entered RESET")

        # Transition to INIT
        self.mode = Modes.INIT

    def get_recipe_environment(self, minute: int):
        """Gets environment object from database for provided minute."""
        return (
            RecipeTransitionModel.objects.filter(minute__lte=minute).order_by(
                "-minute"
            ).first()
        )

    def store_recipe_transitions(self, recipe_transitions):
        """Stores recipe transitions in database."""

        # Clear recipe transition table in database
        RecipeTransitionModel.objects.all().delete()

        # Create recipe transition entries
        for transition in recipe_transitions:
            RecipeTransitionModel.objects.create(
                minute=transition["minute"],
                phase=transition["phase"],
                cycle=transition["cycle"],
                environment_name=transition["environment_name"],
                environment_state=transition["environment_state"],
            )

    def update_recipe_environment(self):
        """ Updates recipe environment. """
        self.logger.debug("Updating recipe environment")
        self.last_update_minute = (
            self.current_timestamp_minutes - self.start_timestamp_minutes
        )
        environment = self.get_recipe_environment(self.last_update_minute)
        self.current_phase = environment.phase
        self.current_cycle = environment.cycle
        self.current_environment_name = environment.environment_name
        self.current_environment_state = environment.environment_state

    def clear_desired_sensor_state(self):
        """ Sets desired sensor state to null values. """
        with self.state.lock:
            for variable in self.state.environment["sensor"]["desired"]:
                self.state.environment["sensor"]["desired"][variable] = None

    def clear_recipe_state(self):
        """Sets recipe state to null values."""
        self.recipe_name = None
        self.recipe_uuid = None
        self.duration_minutes = None
        self.last_update_minute = None
        self.start_timestamp_minutes = None
        self.current_phase = None
        self.current_cycle = None
        self.current_environment_name = None
        self.current_environment_state = {}
        self.stored_mode = None

    def new_minute(self):
        """Check if system clock is on a new minute."""
        current_minute = self.current_timestamp_minutes - self.start_timestamp_minutes
        last_update_minute = self.state.recipe["last_update_minute"]
        if current_minute > last_update_minute:
            return True
        else:
            return False

    def get_duration_string(self, duration_minutes):
        """Converts duration in minutes to duration day-hour-minute string."""
        days = int(float(duration_minutes) / (60 * 24))
        hours = int((float(duration_minutes) - days * 60 * 24) / 60)
        minutes = duration_minutes - days * 60 * 24 - hours * 60
        string = "{} Days {} Hours {} Minutes".format(days, hours, minutes)
        return string

    def set_desired_sensor_values(self, environment_dict):
        """Sets desired sensor values from provided environment dict."""
        with self.state.lock:
            for variable in environment_dict:
                value = environment_dict[variable]
                self.state.environment["sensor"]["desired"][variable] = value
