# Import standard python modules
import copy, glob, json, logging, os, shutil, sys, threading, datetime, time, traceback, ast, socket

# Import device utilities
from device.utilities.accessors import get_nested_dict_safely

# Import the IoT communications class
from device.iot.pubsub import IoTPubSub


# TODO Notes:
# Remove redundant functions accross connect, iot, update, resource, and upgrade
# Adjust function and variable names to match python conventions
# Add static type checking
# Write tests
# Catch specific exceptions
# Pull out file path strings to top of file
# We may just want many of these functions in the manager or in device utilities
# Inherit from state machine manager
# Always use get method to access dicts unless checking for KeyError (rare cases)
# Always use decorators to access shared state w/state.lock
# Use logger class from device utilities
# Reset IotManager or MQTT / Pubsub connection on network reconnect?


# Import device utilities
from device.utilities.statemachine import manager
from device.utilities.state.main import State
from device.utilities import system as system_utilities

# Import device managers
from device.recipe.manager import RecipeManager

# Import manager elements
from device.iot import modes

# Initialize file paths
DEVICE_ID_PATH = "data/registration/device_id.txt"
IMAGES_DIR = "data/images/"
STORED_IMAGES_DIR = "data/images/stored/"


class IotManager(manager.StateMachineManager):
    """Manages IoT communications to the Google cloud backend MQTT service."""

    # Keep track of the previous values that we have published.
    # We only publish a value if it changes.
    prev_env_vars = None
    last_status = datetime.datetime.utcnow()

    def __init__(self, state: State, recipe: RecipeManager) -> None:
        """Initializes iot manager."""

        # Initialize parent class
        super().__init__()

        # Initialize parameters
        self.state = state
        self.recipe = recipe

        # Initialize logger
        self.logger = logger.Logger("IotManager", "iot")
        self.logger.debug("Initializing manager")

        # Initialize our state variables
        self.received_message_count = 0
        self.published_message_count = 0

        # Initialize state machine transitions
        self.transitions: Dict[str, List[str]] = {
            modes.INIT: [
                modes.REGISTERED, modes.UNREGISTERED, modes.ERROR, modes.SHUTDOWN
            ],
            modes.UNREGISTERED: [modes.REGISTERED, modes.ERROR, modes.SHUTDOWN],
            modes.REGISTERED: [modes.INIT, modes.SHUTDOWN, modes.ERROR],
            modes.ERROR: [modes.SHUTDOWN],
        }

        # Initialize state machine mode
        self.mode = modes.INIT

    @property
    def is_registered(self) -> bool:
        """Gets value."""
        return self.state.iot.get("is_registered", False)  # type: ignore

    @is_registered.setter
    def is_registered(self, value: bool) -> None:
        """Safely updates value in shared state."""
        with self.state.lock:
            self.state.iot["is_registered"] = value

    @property
    def device_id(self) -> str:
        """Gets value."""
        return self.state.iot.get("device_id", "Unknown")  # type: ignore

    @device_id.setter
    def device_id(self, value: str) -> None:
        """Safely updates value in shared state."""
        with self.state.lock:
            self.state.iot["device_id"] = value

    @property
    def received_message_count(self) -> int:
        """Gets value."""
        return self.state.iot.get("received_message_count", 0)  # type: ignore

    @received_message_count.setter
    def received_message_count(self, value: int) -> None:
        """Safely updates value in shared state."""
        with self.state.lock:
            self.state.iot["received_message_count"] = value

    @property
    def published_message_count(self) -> int:
        """Gets value."""
        return self.state.iot.get("published_message_count", 0)  # type: ignore

    @published_message_count.setter
    def published_message_count(self, value: int) -> None:
        """Safely updates value in shared state."""
        with self.state.lock:
            self.state.iot["published_message_count"] = value

    ##### STATE MACHINE FUNCTIONS ######################################################

    def run(self) -> None:
        """Runs state machine."""

        # Loop forever
        while True:

            # Check if manager is shutdown
            if self.is_shutdown:
                break

            # Check for mode transitions
            if self.mode == modes.INIT:
                self.run_init_mode()
            elif self.mode == modes.UNREGISTERED:
                self.run_unregistered_mode()
            elif self.mode == modes.REGISTERED:
                self.run_registered_mode()
            elif self.mode == modes.ERROR:
                self.run_error_mode()  # defined in parent classs
            elif self.mode == modes.SHUTDOWN:
                self.run_shutdown_mode()  # defined in parent class
            else:
                self.logger.critical("Invalid state machine mode")
                self.mode = modes.INVALID
                self.is_shutdown = True
                break

    def run_init_mode(self) -> None:
        """Runs init mode."""
        self.logger.debug("Entered INIT")

        # Connect to mqtt service
        self.mqtt = MQTT(..., ..., ...)

        # Publish boot message
        self.publish_boot_message()

        # Transition to normal mode on next state machine update
        self.mode = modes.NORMAL

    def run_unregistered_mode(self) -> None:
        """Runs unregistered mode."""
        self.logger.debug("Entered UNREGISTERED")

        # Initialize timing variables
        last_update_time = 0.0
        update_interval = 15  # seconds

        # Loop forever
        while True:

            # Update registration every update interval
            if time.time() - last_update_time > update_interval:
                last_update_time = time.time()
                self.update_registration()

            # Check for events
            self.check_events()

            # Check for transitions
            if self.new_transition(modes.NORMAL):
                break

            # Update every 100ms
            time.sleep(0.1)

    def run_registered_mode(self) -> None:
        """Runs registered mode."""
        self.logger.debug("Entered REGISTERED")

        # Initialize timing variables
        last_update_time = 0.0
        update_interval = 300  # seconds -> 5 minutes

        # Loop forever
        while True:

            # Publish system summary and images every update interval
            if time.time() - last_update_time > update_interval:
                last_update_time = time.time()
                self.publish_system_summary()
                self.publish_images()

            # Process network events?
            self.iot.process_network_events()

            # Check for events
            self.check_events()

            # Check for transitions
            if self.new_transition(modes.NORMAL):
                break

            # Update every 100ms
            time.sleep(0.1)

    ##### HELPER FUNCTIONS #############################################################

    def publish_boot_message(self) -> None:
        """Publishes boot message."""
        self.logger.debug("Publishing boot message")

        # Build boot message
        boot_message = {
            "device_config": system_utilities.device_config_name(),
            "package_version": self.state.upgrade.get("current_version"),
            "IP": self.state.network.get("ip_address"),
        }

        # Publish boot message
        self.logger.debug("Publised boot message: {}".format(boot_message))
        self.iot.publish_command_reply("boot", json.dumps(boot_message))

    def update_registration(self) -> None:
        """Updates registration information."""
        self.logger.debug("Updating registration")

        # Get device id from file if exists
        self.device_id = self._device_id()

        # Update environment variable, do we actually need this?
        os.environ["DEVICE_ID"] = device_id

        # Check if device id is valid
        if self.device_id != "Unknown":

            # Transition to registered mode on next state machine update
            self.mode = modes.REGISTERED

    def _device_id(self) -> str:
        """Gets device id if it exists at device id path."""
        self.logger.debug("Getting device id")

        # Get device id
        if os.path.exists(DEVICE_ID_PATH):
            with open(DEVICE_ID_PATH) as f:
                device_id = f.readline().strip()
        else:
            device_id = "Unknown"

        # Successfully got device id
        self.logger.debug("Device ID: {}".format(device_id))
        return device_id

    def publish_system_summary(self) -> None:
        """Publishes system summary."""
        self.logger.debug("Publishing summary")

        # Build summary
        recipe_percent_complete_string = self.state.recipe.get(
            "percent_complete_string"
        )
        recipe_time_remaining_minutes = self.state.recipe.get("time_remaining_minutes")
        recipe_time_remaining_string = self.state.recipe.get("time_remaining_string")
        recipe_time_elapsed_string = self.state.recipe.get("time_elapsed_string")
        summary = {
            "timestamp": time.strftime("%FT%XZ", time.gmtime()),
            "IP": system_utilities.ip_address(),
            "package_version": self.state.upgrade.get("current_version"),
            "device_config": system_utilities.device_config_name(),
            "internet_connection": self.state.network.get("is_connected"),
            "memory_available": self.state.resource.get("free_memory"),
            "disk_available": self.state.resource.get("available_disk_space"),
            "iot_received_message_count": self.received_message_count,
            "iot_published_message_count": self.published_message_count,
            "recipe_percent_complete": self.state.recipe.get("percent_complete"),
            "recipe_percent_complete_string": recipe_perent_complete_string,
            "recipe_time_remaining_minutes": recipe_time_remaining_minutes,
            "recipe_time_remaining_string": recipe_time_remaining_string,
            "recipe_time_elapsed_string": recipe_time_elapsed_string,
        }

        # Publish summary
        self.logger.debug("Publishing summary: {}".format(summary))
        self.iot.publish_command_reply("status", json.dumps(summary))

    def publish_environmental_variables(self):
        """Publishes environmental variables."""
        self.logger.debug("Publishing environmental variables")

        # Get environmental variables
        keys = ["reported_sensor_stats", "individual", "instantaneous"]
        environment_variables = get_nested_dict_safely(self.state.environment, keys)

        # Ensure environment variables is a dict
        if environment_variables == None:
            environment_variables = {}

        # Keep a copy of the first set of values (usually None). Why?
        if self.prev_environment_variables is None:
            self.environment_variables = copy.deepcopy(environment_variables)

        # For each value, only publish the ones that have changed.
        for name, value in environment_variables.items():
            if self.prev_environment_variables[name] != value:
                self.environment_variables[name] = copy.deepcopy(value)
                self.iot.publish_env_var(name, value)

    def publish_images(self) -> None:
        """Publishes images in the images directory. On successful publish, moves them 
        to the stored images directory."""
        self.logger.debug("Publishing images")

        # Check for images to publish
        try:
            image_file_list = glob.glob(IMAGES_DIR + "*.png")
            for image_file in image_file_list:

                # Is this file open by a process? (fswebcam)
                if os.system("lsof -f -- {} > /dev/null 2>&1".format(image_file)) == 0:
                    continue  # Yes, so skip it and try the next one.

                # 2018-06-15-T18:34:45Z_Camera-Top.png
                fn1 = image_file.split("_")
                fn2 = fn1[1]  # Camera-Top.png
                fn3 = fn2.split(".")
                camera_name = fn3[0]  # Camera-Top

                # Get the file contents
                f = open(image_file, "rb")
                file_bytes = f.read()
                f.close()

                # If the size is < 200KB, then it is garbage we delete
                # (based on the 1280x1024 average file size)
                if len(file_bytes) < 200000:
                    os.remove(image_file)
                    continue

                self.iot.publish_binary_image(camera_name, "png", file_bytes)

                # Check if stored directory exists, if not create it
                if not os.path.isdir(STORED_IMAGES_DIR):
                    os.mkdir(STORED_IMAGES_DIR)

                # Move image from image directory once processed
                stored_image_file = image_file.replace(IMAGES_DIR, STORED_IMAGES_DIR)
                shutil.move(image_file, stored_image_file)

        except Exception as e:
            message = "Unable to publish images, unhandled exception: {}".format(e)
            self.logger.exception(message)

    ##### EVENT FUNCTIONS ##############################################################

    def reset(self) -> None:
        """Resets iot pubsub. TODO: Should probably be in the pubsub (or mqtt) class."""
        try:
            # Pass in the callback that receives commands
            self.iot = IoTPubSub(self, self.command_received, self.state.iot)
        except Exception as e:
            self.iot = None
            message = "Unable to reset, unhandled exception".format(type(e))
            self.logger.exception(message)
            self.mode = modes.ERROR

    def publish_message(self, name, msg_json) -> None:
        """Send a command reply. TODO: Not sure where this is used."""
        if self.iot is None:
            return
        self.iot.publish_command_reply(name, msg_json)

    def command_received(self, command, arg0, arg1):
        """Process commands received from the backend (UI). This is a callback that is 
        called by the IoTPubSub class when this device receives commands from the UI."""

        if None == self.iot:
            return

        try:
            if command == IoTPubSub.CMD_START:
                recipe_json = arg0
                recipe_dict = json.loads(arg0)

                # Make sure we have a valid recipe uuid
                if (
                    "uuid" not in recipe_dict
                    or None == recipe_dict["uuid"]
                    or 0 == len(recipe_dict["uuid"])
                ):
                    self.logger.error("command_received: missing recipe UUID")
                    return
                recipe_uuid = recipe_dict["uuid"]

                # First stop any recipe that may be running
                self.recipe.stop_recipe()

                # Put this recipe via recipe manager
                self.recipe.create_or_update_recipe(recipe_json)

                # Start this recipe via recipe manager
                self.recipe.start_recipe(recipe_uuid)

                # Record that we processed this command
                self.iot.publish_command_reply(command, recipe_json)
                return

            if command == IoTPubSub.CMD_STOP:
                self.recipe.stop_recipe()
                self.iot.publish_command_reply(command, "")
                return

            self.logger.error("command_received: Unknown command: {}".format(command))
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.logger.critical("Exception in command_received(): %s" % e)
            traceback.print_tb(exc_traceback, file=sys.stdout)
            return False
