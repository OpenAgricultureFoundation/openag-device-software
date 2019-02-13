# Import python modules
import logging, time, threading, os, sys, datetime, json, jsonschema

# Import python types
from typing import Optional, List, Dict, Any, Tuple

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.statemachine.manager import StateMachineManager

# Import device state
from device.utilities.state.main import State

# Import database models
from app import models

# Import manager elements
from device.recipe import modes, events

# Set file paths
RECIPE_SCHEMA_PATH = "data/schemas/recipe.json"


class RecipeManager(StateMachineManager):
    """Manages recipe state machine thread."""

    def __init__(self, state: State) -> None:
        """Initializes recipe manager."""

        # Initialize parent class
        super().__init__()

        # Initialize logger
        self.logger = Logger("Recipe", "recipe")

        # Initialize state
        self.state = state

        # Initialize state machine transitions
        self.transitions = {
            modes.INIT: [modes.NORECIPE, modes.ERROR],
            modes.NORECIPE: [modes.START, modes.ERROR],
            modes.START: [modes.QUEUED, modes.ERROR],
            modes.QUEUED: [modes.NORMAL, modes.STOP, modes.ERROR],
            modes.NORMAL: [modes.PAUSE, modes.STOP, modes.ERROR],
            modes.PAUSE: [modes.START, modes.ERROR],
            modes.STOP: [modes.NORECIPE, modes.ERROR],
            modes.ERROR: [modes.RESET],
            modes.RESET: [modes.INIT],
        }

        # Start state machine from init mode
        self.mode = modes.INIT

    @property
    def mode(self) -> str:
        """Gets mode value. Important to keep this local so all
        state transitions only occur from within thread."""
        return self._mode

    @mode.setter
    def mode(self, value: str) -> None:
        """Safely updates recipe mode in shared state."""
        self._mode = value
        with self.state.lock:
            self.state.recipe["mode"] = value

    @property
    def stored_mode(self) -> Optional[str]:
        """Gets the stored mode from shared state."""
        value = self.state.recipe.get("stored_mode")
        if value != None:
            return str(value)
        else:
            return None

    @stored_mode.setter
    def stored_mode(self, value: Optional[str]) -> None:
        """Safely updates stored mode in shared state."""
        with self.state.lock:
            self.state.recipe["stored_mode"] = value

    @property
    def recipe_uuid(self) -> Optional[str]:
        """Gets recipe uuid from shared state."""
        value = self.state.recipe.get("recipe_uuid")
        if value != None:
            return str(value)
        else:
            return None

    @recipe_uuid.setter
    def recipe_uuid(self, value: Optional[str]) -> None:
        """Safely updates recipe uuid in shared state."""
        with self.state.lock:
            self.state.recipe["recipe_uuid"] = value

    @property
    def recipe_name(self) -> Optional[str]:
        """Gets recipe name from shared state."""
        value = self.state.recipe.get("recipe_name")
        if value != None:
            return str(value)
        else:
            return None

    @recipe_name.setter
    def recipe_name(self, value: Optional[str]) -> None:
        """ afely updates recipe name in shared state."""
        with self.state.lock:
            self.state.recipe["recipe_name"] = value

    @property
    def is_active(self) -> bool:
        """Gets value."""
        return self.state.recipe.get("is_active", False)  # type: ignore

    @is_active.setter
    def is_active(self, value: bool) -> None:
        """Safely updates value in shared state."""
        with self.state.lock:
            self.state.recipe["is_active"] = value

    @property
    def current_timestamp_minutes(self) -> int:
        """ Get current timestamp in minutes. """
        return int(time.time() / 60)

    @property
    def start_timestamp_minutes(self) -> Optional[int]:
        """ Gets start timestamp minutes from shared state. """
        value = self.state.recipe.get("start_timestamp_minutes")
        if value != None:
            return int(value)  # type: ignore
        else:
            return None

    @start_timestamp_minutes.setter
    def start_timestamp_minutes(self, value: Optional[int]) -> None:
        """Generates start datestring then safely updates start timestamp 
        minutes and datestring in shared state."""

        # Define var type
        start_datestring: Optional[str]

        # Generate start datestring
        if value != None:
            val_int = int(value)  # type: ignore
            start_datestring = (
                datetime.datetime.fromtimestamp(val_int * 60).strftime(
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
    def start_datestring(self) -> Optional[str]:
        """Gets start datestring value from shared state."""
        return self.state.recipe.get("start_datestring")  # type: ignore

    @property
    def duration_minutes(self) -> Optional[int]:
        """Gets recipe duration in minutes from shared state."""
        return self.state.recipe.get("duration_minutes")  # type: ignore

    @duration_minutes.setter
    def duration_minutes(self, value: Optional[int]) -> None:
        """Generates duration string then safely updates duration string 
        and minutes in shared state. """

        # Define var type
        duration_string: Optional[str]

        # Generate duation string
        if value != None:
            duration_string = self.get_duration_string(value)  # type: ignore
        else:
            duration_string = None

        # Safely update duration minutes and string in shared state
        with self.state.lock:
            self.state.recipe["duration_minutes"] = value
            self.state.recipe["duration_string"] = duration_string

    @property
    def last_update_minute(self) -> Optional[int]:
        """Gets the last update minute from shared state."""
        return self.state.recipe.get("last_update_minute")  # type: ignore

    @last_update_minute.setter
    def last_update_minute(self, value: Optional[int]) -> None:
        """Generates percent complete, percent complete string, time
        remaining minutes, time remaining string, and time elapsed
        string then safely updates last update minute and aforementioned
        values in shared state. """

        # Define var types
        percent_complete_string: Optional[float]
        time_remaining_string: Optional[str]
        time_elapsed_string: Optional[str]

        # Generate values
        if value != None and self.duration_minutes != None:
            percent_complete = (
                float(value) / self.duration_minutes * 100  # type: ignore
            )
            percent_complete_string = "{0:.2f} %".format(  # type: ignore
                percent_complete
            )
            time_remaining_minutes = self.duration_minutes - value  # type: ignore
            time_remaining_string = self.get_duration_string(time_remaining_minutes)
            time_elapsed_string = self.get_duration_string(value)  # type: ignore
        else:
            percent_complete = None  # type: ignore
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
    def percent_complete(self) -> Optional[float]:
        """Gets percent complete from shared state."""
        return self.state.recipe.get("percent_complete")  # type: ignore

    @property
    def percent_complete_string(self) -> Optional[str]:
        """Gets percent complete string from shared state."""
        return self.state.recipe.get("percent_complete_string")  # type: ignore

    @property
    def time_remaining_minutes(self) -> Optional[int]:
        """Gets time remaining minutes from shared state."""
        return self.state.recipe.get("time_remaining_minutes")  # type: ignore

    @property
    def time_remaining_string(self) -> Optional[str]:
        """Gets time remaining string from shared state."""
        return self.state.recipe.get("time_remaining_string")  # type: ignore

    @property
    def time_elapsed_string(self) -> Optional[str]:
        """Gets time elapsed string from shared state."""
        value = self.state.recipe.get("time_elapsed_string")
        if value != None:
            return str(value)
        else:
            return None

    @property
    def current_phase(self) -> Optional[str]:
        """Gets the recipe current phase from shared state."""
        value = self.state.recipe.get("current_phase")
        if value != None:
            return str(value)
        else:
            return None

    @current_phase.setter
    def current_phase(self, value: str) -> None:
        """Safely updates current phase in shared state."""
        with self.state.lock:
            self.state.recipe["current_phase"] = value

    @property
    def current_cycle(self) -> Optional[str]:
        """Gets the current cycle from shared state."""
        value = self.state.recipe.get("current_cycle")
        if value != None:
            return str(value)
        else:
            return None

    @current_cycle.setter
    def current_cycle(self, value: Optional[str]) -> None:
        """Safely updates current cycle in shared state."""
        with self.state.lock:
            self.state.recipe["current_cycle"] = value

    @property
    def current_environment_name(self) -> Optional[str]:
        """Gets the current environment name from shared state"""
        value = self.state.recipe.get("current_environment_name")
        if value != None:
            return str(value)
        else:
            return None

    @current_environment_name.setter
    def current_environment_name(self, value: Optional[str]) -> None:
        """Safely updates current environment name in shared state."""
        with self.state.lock:
            self.state.recipe["current_environment_name"] = value

    @property
    def current_environment_state(self) -> Any:
        """Gets the current environment state from shared state."""
        return self.state.recipe.get("current_environment_name")

    @current_environment_state.setter
    def current_environment_state(self, value: Optional[Dict]) -> None:
        """ Safely updates current environment state in shared state. """
        with self.state.lock:
            self.state.recipe["current_environment_state"] = value
            self.set_desired_sensor_values(value)  # type: ignore

    ##### STATE MACHINE FUNCTIONS ######################################################

    def run(self) -> None:
        """Runs state machine."""

        # Loop forever
        while True:

            # Check if thread is shutdown
            if self.is_shutdown:
                break

            # Check for mode transitions
            if self.mode == modes.INIT:
                self.run_init_mode()
            if self.mode == modes.NORECIPE:
                self.run_norecipe_mode()
            elif self.mode == modes.START:
                self.run_start_mode()
            elif self.mode == modes.QUEUED:
                self.run_queued_mode()
            elif self.mode == modes.NORMAL:
                self.run_normal_mode()
            elif self.mode == modes.PAUSE:
                self.run_pause_mode()
            elif self.mode == modes.STOP:
                self.run_stop_mode()
            elif self.mode == modes.RESET:
                self.run_reset_mode()
            elif self.mode == modes.ERROR:
                self.run_error_mode()
            elif self.mode == modes.SHUTDOWN:
                self.run_shutdown_mode()
            else:
                self.logger.critical("Invalid state machine mode")
                self.mode = modes.INVALID
                self.is_shutdown = True
                break

    def run_init_mode(self) -> None:
        """Runs initialization mode. Checks for stored recipe mode and transitions to
        mode if exists, else transitions to no recipe mode."""
        self.logger.info("Entered INIT")

        # Initialize state
        self.is_active = False

        # Check for stored mode
        mode = self.state.recipe.get("stored_mode")
        if mode != None:
            self.logger.debug("Returning to stored mode: {}".format(mode))
            self.mode = mode  # type: ignore
        else:
            self.mode = modes.NORECIPE

    def run_norecipe_mode(self) -> None:
        """Runs no recipe mode. Clears recipe and desired sensor state then waits for
        new events and transitions."""
        self.logger.info("Entered NORECIPE")

        # Set run state
        self.is_active = False

        # Clear state
        self.clear_recipe_state()
        self.clear_desired_sensor_state()

        # Loop forever
        while True:

            # Check for events
            self.check_events()

            # Check for transitions
            if self.new_transition(modes.NORECIPE):
                break

            # Update every 100ms
            time.sleep(0.1)

    def run_start_mode(self) -> None:
        """Runs start mode. Loads commanded recipe uuid into shared state, 
        retrieves recipe json from recipe table, generates recipe 
        transitions, stores them in the recipe transitions table, extracts
        recipe duration and start time then transitions to queued mode."""

        # Set run state
        self.is_active = True

        try:
            self.logger.info("Entered START")

            # Get recipe json from recipe uuid
            recipe_json = models.RecipeModel.objects.get(uuid=self.recipe_uuid).json
            recipe_dict = json.loads(recipe_json)

            # Parse recipe transitions
            transitions = self.parse(recipe_dict)

            # Store recipe transitions in database
            self.store_recipe_transitions(transitions)

            # Set recipe duration
            self.duration_minutes = transitions[-1]["minute"]

            # Set recipe name
            self.recipe_name = recipe_dict["name"]
            self.logger.info("Started: {}".format(self.recipe_name))

            # Transition to queued mode
            self.mode = modes.QUEUED

        except Exception as e:
            message = "Unable to start recipe, unhandled exception {}".format(e)
            self.logger.critical(message)
            self.mode = modes.NORECIPE

    def run_queued_mode(self) -> None:
        """Runs queued mode. Waits for recipe start timestamp to be greater than
        or equal to current timestamp then transitions to NORMAL."""
        self.logger.info("Entered QUEUED")

        # Set state
        self.is_active = True

        # Initialize time counter
        prev_time_seconds = 0.0

        # Loop forever
        while True:

            # Check if recipe is ready to run
            current = self.current_timestamp_minutes
            start = self.start_timestamp_minutes
            if current >= start:  # type: ignore
                self.mode = modes.NORMAL
                break

            # Calculate remaining delay time
            delay_minutes = start - current  # type: ignore

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
            if self.new_transition(modes.QUEUED):
                break

            # Update every 100ms
            time.sleep(0.1)

    def run_normal_mode(self) -> None:
        """ Runs normal mode. Updates recipe and environment states every minute. 
        Checks for events and transitions."""
        self.logger.info("Entered NORMAL")

        # Set state
        self.is_active = True

        # Update recipe environment on first entry
        self.update_recipe_environment()

        # Loop forever
        while True:

            # Update recipe and environment states every minute
            if self.new_minute():
                self.update_recipe_environment()

            # Check for recipe end
            if self.current_phase == "End" and self.current_cycle == "End":
                self.logger.info("Recipe is over, so transitions from NORMAL to STOP")
                self.mode = modes.STOP
                break

            # Check for events
            self.check_events()

            # Check for transitions
            if self.new_transition(modes.NORMAL):
                break

            # Update every 100ms
            time.sleep(0.1)

    def run_pause_mode(self) -> None:
        """Runs pause mode. Clears recipe and desired sensor state, waits for new 
        events and transitions."""
        self.logger.info("Entered PAUSE")

        # Set state
        self.is_active = True

        # Clear recipe and desired sensor state
        self.clear_recipe_state()
        self.clear_desired_sensor_state()

        # Loop forever
        while True:

            # Check for events
            self.check_events()

            # Check for transitions
            if self.new_transition(modes.PAUSE):
                break

            # Update every 100ms
            time.sleep(0.1)

    def run_stop_mode(self) -> None:
        """Runs stop mode. Clears recipe and desired sensor state then transitions
        to no recipe mode."""
        self.logger.info("Entered STOP")

        # Clear recipe and desired sensor states
        self.clear_recipe_state()
        self.clear_desired_sensor_state()

        # Set state
        self.is_active = False

        # Transition to NORECIPE
        self.mode = modes.NORECIPE

    def run_error_mode(self) -> None:
        """Runs error mode. Clears recipe state and desired sensor state then waits 
        for new events and transitions."""
        self.logger.info("Entered ERROR")

        # Clear recipe and desired sensor states
        self.clear_recipe_state()
        self.clear_desired_sensor_state()

        # Set state
        self.is_active = False

        # Loop forever
        while True:

            # Check for events
            self.check_events()

            # Check for transitions
            if self.new_transition(modes.ERROR):
                break

            # Update every 100ms
            time.sleep(0.1)

    def run_reset_mode(self) -> None:
        """Runs reset mode. Clears error state then transitions to init mode."""
        self.logger.info("Entered RESET")

        # Transition to INIT
        self.mode = modes.INIT

    ##### HELPER FUNCTIONS #############################################################

    def get_recipe_environment(self, minute: int) -> Any:
        """Gets environment object from database for provided minute."""
        return (
            models.RecipeTransitionModel.objects.filter(minute__lte=minute)
            .order_by("-minute")
            .first()
        )

    def store_recipe_transitions(self, recipe_transitions: List) -> None:
        """Stores recipe transitions in database."""

        # Clear recipe transitions table in database
        models.RecipeTransitionModel.objects.all().delete()

        # Create recipe transitions entries
        for transitions in recipe_transitions:
            models.RecipeTransitionModel.objects.create(
                minute=transitions["minute"],
                phase=transitions["phase"],
                cycle=transitions["cycle"],
                environment_name=transitions["environment_name"],
                environment_state=transitions["environment_state"],
            )

    def update_recipe_environment(self) -> None:
        """ Updates recipe environment. """
        self.logger.debug("Updating recipe environment")

        current = self.current_timestamp_minutes
        start = self.start_timestamp_minutes
        self.last_update_minute = current - start  # type: ignore
        environment = self.get_recipe_environment(self.last_update_minute)
        self.current_phase = environment.phase
        self.current_cycle = environment.cycle
        self.current_environment_name = environment.environment_name
        self.current_environment_state = environment.environment_state

    def clear_desired_sensor_state(self) -> None:
        """ Sets desired sensor state to null values. """
        with self.state.lock:
            for variable in self.state.environment["sensor"]["desired"]:
                self.state.environment["sensor"]["desired"][variable] = None

    def clear_recipe_state(self) -> None:
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

    def new_minute(self) -> bool:
        """Check if system clock is on a new minute."""
        current = self.current_timestamp_minutes
        start = self.start_timestamp_minutes
        current_minute = current - start  # type: ignore
        last_update_minute = self.state.recipe["last_update_minute"]
        if current_minute > last_update_minute:
            return True
        else:
            return False

    def get_duration_string(self, duration_minutes: int) -> str:
        """Converts duration in minutes to duration day-hour-minute string."""
        days = int(float(duration_minutes) / (60 * 24))
        hours = int((float(duration_minutes) - days * 60 * 24) / 60)
        minutes = int(duration_minutes - days * 60 * 24 - hours * 60)
        string = "{} Days {} Hours {} Minutes".format(days, hours, minutes)
        return string

    def set_desired_sensor_values(self, environment_dict: Dict) -> None:
        """Sets desired sensor values from provided environment dict."""
        with self.state.lock:
            for variable in environment_dict:
                value = environment_dict[variable]
                self.state.environment["sensor"]["desired"][variable] = value

    def validate(
        self, json_: str, should_exist: Optional[bool] = None
    ) -> Tuple[bool, Optional[str]]:
        """Validates a recipe. Returns true if valid."""

        # Load recipe schema
        schema = json.load(open(RECIPE_SCHEMA_PATH))

        # Check valid json and try to parse recipe
        try:
            # Decode json
            recipe = json.loads(json_)

            # Validate recipe against schema
            jsonschema.validate(recipe, schema)

            # Get top level recipe parameters
            format_ = recipe["format"]
            version = recipe["version"]
            name = recipe["name"]
            uuid = recipe["uuid"]
            cultivars = recipe["cultivars"]
            cultivation_methods = recipe["cultivation_methods"]
            environments = recipe["environments"]
            phases = recipe["phases"]

        except json.decoder.JSONDecodeError as e:
            message = "Invalid recipe json encoding: {}".format(e)
            self.logger.debug(message)
            return False, message
        except jsonschema.exceptions.ValidationError as e:
            message = "Invalid recipe json schema: {}".format(e.message)
            self.logger.debug(message)
            return False, message
        except KeyError as e:
            self.logger.critical("Recipe schema did not ensure `{}` exists".format(e))
            message = "Invalid recipe json schema: `{}` is requred".format(e)
            return False, message
        except Exception as e:
            self.logger.critical("Invalid recipe, unhandled exception: {}".format(e))
            return False, "Unhandled exception: {}".format(type(e))

        # Check valid uuid
        if uuid == None or len(uuid) == 0:
            return False, "Invalid uuid"

        # Check recipe existance criteria, does not check if should_exist == None
        recipe_exists = models.RecipeModel.objects.filter(uuid=uuid).exists()
        if should_exist == True and not recipe_exists:
            return False, "UUID does not exist"
        elif should_exist == False and recipe_exists:
            return False, "UUID already exists"

        # Check cycle environment key names are valid
        try:
            for phase in phases:
                for cycle in phase["cycles"]:
                    cycle_name = cycle["name"]
                    environment_key = cycle["environment"]
                    if environment_key not in environments:
                        message = "Invalid environment key `{}` in cycle `{}`".format(
                            environment_key, cycle_name
                        )
                        self.logger.debug(message)
                        return False, message
        except KeyError as e:
            self.logger.critical("Recipe schema did not ensure `{}` exists".format(e))
            message = "Invalid recipe json schema: `{}` is requred".format(e)
            return False, message

        # Build list of environment variables
        env_vars: List[str] = []
        for env_key, env_dict in environments.items():
            for env_var, _ in env_dict.items():
                if env_var != "name" and env_var not in env_vars:
                    env_vars.append(env_var)

        # Check environment variables are valid sensor variables
        for env_var in env_vars:
            if not models.SensorVariableModel.objects.filter(key=env_var).exists():
                message = "Invalid recipe environment variable: `{}`".format(env_var)
                self.logger.debug(message)
                return False, message

        """
        TODO: Reinstate these checks once cloud system has support for enforcing
        uniqueness of cultivars and cultivation methods. While we are at it, my as 
        well do the same for variable types so can create "scientific" recipes from 
        the cloud UI and send complete recipes. Cloud system will need a way to manage
        recipes and recipe derivatives. R.e. populating cultivars table, might just 
        want to scrape seedsavers or leverage another existing organism database. 
        Probably also want to think about organismal groups (i.e. classifications).
        Classifications could the standard scientific (Kingdom , Phylum, etc.) or a more
        user-friendly group (e.g. Leafy Greens, Six-Week Grows, Exotic Plants, 
        Pre-Historic Plants, etc.)


        # Check cultivars are valid
        for cultivar in cultivars:
            cultivar_name = cultivar["name"]
            cultivar_uuid = cultivar["uuid"]
            if not models.CultivarModel.objects.filter(uuid=cultivar_uuid).exists():
                message = "Invalid recipe cultivar: `{}`".format(cultivar_name)
                self.logger.debug(message)
                return False, message

        # Check cultivation methods are valid
        for method in cultivation_methods:
            method_name = method["name"]
            method_uuid = method["uuid"]
            if not models.CultivationMethodModel.objects.filter(
                uuid=method_uuid
            ).exists():
                message = "Invalid recipe cultivation method: `{}`".format(method_name)
                self.logger.debug(message)
                return False, message

        """

        # Recipe is valid
        return True, None

    def parse(self, recipe: Dict[str, Any]) -> List[Dict[str, Any]]:
        """ Parses recipe into state transitions. """
        transitions = []
        minute_counter = 0
        for phase in recipe["phases"]:
            phase_name = phase["name"]
            for i in range(phase["repeat"]):
                for cycle in phase["cycles"]:
                    # Get environment object and cycle name
                    environment_key = cycle["environment"]
                    environment = recipe["environments"][environment_key]
                    cycle_name = cycle["name"]

                    # Get duration
                    if "duration_hours" in cycle:
                        duration_hours = cycle["duration_hours"]
                        duration_minutes = duration_hours * 60
                    elif "duration_minutes" in cycle:
                        duration_minutes = cycle["duration_minutes"]
                    else:
                        raise KeyError(
                            "Could not find 'duration_minutes' or 'duration_hours' in cycle"
                        )

                    # Make shallow copy of env so we can pop a property locally
                    environment_copy = dict(environment)
                    environment_name = environment_copy["name"]
                    del environment_copy["name"]
                    environment_state = environment_copy

                    # Write recipe transition to database
                    transitions.append(
                        {
                            "minute": minute_counter,
                            "phase": phase_name,
                            "cycle": cycle_name,
                            "environment_name": environment_name,
                            "environment_state": environment_state,
                        }
                    )

                    # Increment minute counter
                    minute_counter += duration_minutes

        # Set recipe end
        transitions.append(
            {
                "minute": minute_counter,
                "phase": "End",
                "cycle": "End",
                "environment_name": "End",
                "environment_state": {},
            }
        )

        # Return state transitions
        return transitions

    def check_events(self) -> None:
        """Checks for a new event. Only processes one event per call, even if there are 
        multiple in the queue. Events are processed first-in-first-out (FIFO)."""

        # Check for new events
        if self.event_queue.empty():
            return

        # Get request
        request = self.event_queue.get()
        self.logger.debug("Received new request: {}".format(request))

        # Get request parameters
        try:
            type_ = request["type"]
        except KeyError as e:
            message = "Invalid request parameters: {}".format(e)
            self.logger.exception(message)
            return

        # Execute request
        if type_ == events.START:
            self._start_recipe(request)
        elif type_ == events.STOP:
            self._stop_recipe()
        else:
            self.logger.error("Invalid event request type in queue: {}".format(type_))

    def start_recipe(
        self, uuid: str, timestamp: Optional[float] = None, check_mode: bool = True
    ) -> Tuple[str, int]:
        """Adds a start recipe event to event queue."""
        self.logger.debug("Adding start recipe event to event queue")
        self.logger.debug("Recipe UUID: {}, timestamp: {}".format(uuid, timestamp))

        # Check recipe uuid exists
        if not models.RecipeModel.objects.filter(uuid=uuid).exists():
            message = "Unable to start recipe, invalid uuid"
            return message, 400

        # Check timestamp is valid if provided
        if timestamp != None and timestamp < time.time():  # type: ignore
            message = "Unable to start recipe, timestamp must be in the future"
            return message, 400

        # Check valid mode transition if enabled
        if check_mode and not self.valid_transition(self.mode, modes.START):
            message = "Unable to start recipe from {} mode".format(self.mode)
            self.logger.debug(message)
            return message, 400

        # Add start recipe event request to event queue
        request = {"type": events.START, "uuid": uuid, "timestamp": timestamp}
        self.event_queue.put(request)

        # Successfully added recipe to event queue
        message = "Starting recipe"
        return message, 202

    def _start_recipe(self, request: Dict[str, Any]) -> None:
        """Starts a recipe. Assumes request has been verified in public
        start recipe function."""
        self.logger.debug("Starting recipe")

        # Get request parameters
        uuid = request.get("uuid")
        timestamp = request.get("timestamp")

        # Convert timestamp to minutes if not None
        if timestamp != None:
            timestamp_minutes = int(timestamp / 60.0)  # type: ignore
        else:
            timestamp_minutes = int(time.time() / 60.0)

        # Check valid mode transition
        if not self.valid_transition(self.mode, modes.START):
            self.logger.critical("Tried to start recipe from {} mode".format(self.mode))
            return

        # Start recipe on next state machine update
        self.recipe_uuid = uuid
        self.start_timestamp_minutes = timestamp_minutes
        self.mode = modes.START

    def stop_recipe(self, check_mode: bool = True) -> Tuple[str, int]:
        """Adds stop recipe event to event queue."""
        self.logger.debug("Adding stop recipe event to event queue")

        # Check valid mode transition if enabled
        if check_mode and not self.valid_transition(self.mode, modes.STOP):
            message = "Unable to stop recipe from {} mode".format(self.mode)
            self.logger.debug(message)
            return message, 400

        # Put request into queue
        request = {"type": events.STOP}
        self.event_queue.put(request)

        # Successfully added stop recipe to event queue
        message = "Stopping recipe"
        return message, 200

    def _stop_recipe(self) -> None:
        """Stops a recipe. Assumes request has been verified in public
        stop recipe function."""
        self.logger.debug("Stopping recipe")

        # Check valid mode transition
        if not self.valid_transition(self.mode, modes.STOP):
            self.logger.critical("Tried to stop recipe from {} mode".format(self.mode))
            return

        # Stop recipe on next state machine update
        self.mode = modes.STOP

    def create_recipe(self, json_: str) -> Tuple[str, int]:
        """Creates a recipe into database."""
        self.logger.debug("Creating recipe")

        # Check if recipe is valid
        is_valid, error = self.validate(json_, should_exist=False)
        if not is_valid:
            message = "Unable to create recipe. {}".format(error)
            self.logger.debug(message)
            return message, 400

        # Create recipe in database
        try:
            recipe = json.loads(json_)
            models.RecipeModel.objects.create(json=json.dumps(recipe))
            message = "Successfully created recipe"
            return message, 200
        except:
            message = "Unable to create recipe, unhandled exception"
            self.logger.exception(message)
            return message, 500

    def update_recipe(self, json_: str) -> Tuple[str, int]:
        """Updates an existing recipe in database."""

        # Check if recipe is valid
        is_valid, error = self.validate(json_, should_exist=False)
        if not is_valid:
            message = "Unable to update recipe. {}".format(error)
            self.logger.debug(message)
            return message, 400

        # Update recipe in database
        try:
            recipe = json.loads(json_)
            r = models.RecipeModel.objects.get(uuid=recipe["uuid"])
            r.json = json.dumps(recipe)
            r.save()
            message = "Successfully updated recipe"
            return message, 200
        except:
            message = "Unable to update recipe, unhandled exception"
            self.logger.exception(message)
            return message, 500

    def create_or_update_recipe(self, json_: str) -> Tuple[str, int]:
        """Creates or updates an existing recipe in database."""

        # Check if recipe is valid
        is_valid, error = self.validate(json_, should_exist=None)
        if not is_valid:
            message = "Unable to create/update recipe -> {}".format(error)
            return message, 400

        # Check if creating or updating recipe in database
        recipe = json.loads(json_)
        if not models.RecipeModel.objects.filter(uuid=recipe["uuid"]).exists():

            # Create recipe
            try:
                recipe = json.loads(json_)
                models.RecipeModel.objects.create(json=json.dumps(recipe))
                message = "Successfully created recipe"
                return message, 200
            except:
                message = "Unable to create recipe, unhandled exception"
                self.logger.exception(message)
                return message, 500
        else:

            # Update recipe
            try:
                r = models.RecipeModel.objects.get(uuid=recipe["uuid"])
                r.json = json.dumps(recipe)
                r.save()
                message = "Successfully updated recipe"
                return message, 200
            except:
                message = "Unable to update recipe, unhandled exception"
                self.logger.exception(message)
                return message, 500

    def recipe_exists(self, uuid: str) -> bool:
        """Checks if a recipe exists."""
        return models.RecipeModel.objects.filter(uuid=uuid).exists()
