# Import standard python modules
import sys, os, subprocess, copy, glob, json, shutil, time, datetime

# Import python types
from typing import Dict, Any, Optional, List

# Import device utilities
from device.utilities.statemachine import manager
from device.utilities.state.main import State
from device.utilities import logger, accessors, system, network

# Import device managers
from device.recipe.manager import RecipeManager

# Import manager elements
from device.iot import modes, commands
from device.iot.pubsub import PubSub

# TODO Notes:
# Add static type checking
# Write tests
# Catch specific exceptions
# Reset IotManager or MQTT / Pubsub connection on network reconnect?
# Run through all state tverification_coderansitions and make sure they are reasonable

# Initialize file paths
REGISTRATION_DATA_DIR = "data/registration/"
DEVICE_ID_PATH = REGISTRATION_DATA_DIR + "device_id.bash"
ROOTS_PATH = REGISTRATION_DATA_DIR + "roots.pem"
RSA_CERT_PATH = REGISTRATION_DATA_DIR + "rsa_cert.pem"
RSA_PRIVATE_PATH = REGISTRATION_DATA_DIR + "rsa_private.pem"
VERIFICATION_CODE_PATH = REGISTRATION_DATA_DIR + "verification_code.txt"
IMAGES_DIR = "data/images/"
STORED_IMAGES_DIR = "data/images/stored/"
REGISTER_SCRIPT_PATH = "scripts/one_time_key_creation_and_iot_device_registration.sh"


class IotManager(manager.StateMachineManager):
    """Manages IoT communications to the Google cloud backend MQTT service."""

    # Keep track of the previous values that we have published.
    # We only publish a value if it changes.
    prev_environment_variables = {}
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
        """Gets value. TODO: Move this from file based to state based."""
        return self._is_registered()

    @property
    def verification_code(self) -> str:
        """Gets value. TODO: Move this from file based to state based."""
        try:
            with open(VERIFICATION_CODE_PATH) as f:
                code = f.read().strip()
            return code
        except Exception as e:
            message = "Unable to get verification code, unhandled exception: {}".format(
                type(e)
            )
            self.logger.exception(message)
            return "INVALID"

    @property
    def pubsub_is_connected(self) -> bool:
        """Gets value."""
        return self.state.iot.get("pubsub_is_connected", False)  # type: ignore

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
    def pubsub_received_message_count(self) -> int:
        """Gets value."""
        return self.state.iot.get("pubsub_received_message_count", 0)  # type: ignore

    @property
    def pubsub_published_message_count(self) -> int:
        """Gets value."""
        return self.state.iot.get("pubsub_published_message_count", 0)  # type: ignore

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

        # Connect to pubsub service
        self.pubsub = PubSub(self.state, self.command_received)

        # Publish boot message
        self.publish_boot_message()

        # Give othe managers time to initialize
        time.sleep(10)  # seconds

        # Transition to unregistered mode on next state machine update
        self.mode = modes.UNREGISTERED

    def run_unregistered_mode(self) -> None:
        """Runs unregistered mode."""
        self.logger.debug("Entered UNREGISTERED")

        # Initialize timing variables
        last_update_time = 0.0
        update_interval = 60  # seconds

        # Loop forever
        while True:

            # Update registration every update interval
            if time.time() - last_update_time > update_interval:
                last_update_time = time.time()
                self.update_registration()

            # Check for events
            self.check_events()

            # Check for transitions
            if self.new_transition(modes.UNREGISTERED):
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
                self.publish_environmental_variables()  # TODO: Should we make this every minute?
                self.publish_images()

            # Process network events
            self.pubsub.process_network_events()

            # Check for events
            self.check_events()

            # Check for transitions
            if self.new_transition(modes.REGISTERED):
                break

            # Update every 100ms
            time.sleep(0.1)

    ##### HELPER FUNCTIONS #############################################################

    def publish_boot_message(self) -> None:
        """Publishes boot message."""
        self.logger.debug("Publishing boot message")

        # Build boot message
        boot_message = {
            "device_config": system.device_config_name(),
            "package_version": self.state.upgrade.get("current_version"),
            "IP": self.state.network.get("ip_address"),
        }

        # Publish boot message
        self.logger.debug("Publised boot message: {}".format(boot_message))
        self.pubsub.publish_command_reply("boot", json.dumps(boot_message))

    def update_registration(self) -> None:
        """Updates registration information."""
        self.logger.debug("Updating registration")

        # TODO: This should check if system is connected to internet, if so try to
        # register, then update state vars and transition to registered mode on
        # success or else handle exception on error."""

        # Get device id from file if exists
        self.device_id = self._device_id()

        # Update environment variable, do we actually need this?
        os.environ["DEVICE_ID"] = self.device_id

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
                contents = f.read()
                index = contents.find("=")
                device_id = contents[index + 1:].strip()
        else:
            device_id = "Unknown"

        # Successfully got device id
        self.logger.debug("Device ID: {}".format(device_id))
        return device_id

    def publish_system_summary(self) -> None:
        """Publishes system summary."""
        self.logger.debug("Publishing system summary")

        # Build summary
        recipe_percent_complete_string = self.state.recipe.get(
            "percent_complete_string"
        )
        recipe_time_remaining_minutes = self.state.recipe.get("time_remaining_minutes")
        recipe_time_remaining_string = self.state.recipe.get("time_remaining_string")
        recipe_time_elapsed_string = self.state.recipe.get("time_elapsed_string")
        summary = {
            "timestamp": time.strftime("%FT%XZ", time.gmtime()),
            "IP": self.state.network.get("ip_address"),
            "package_version": self.state.upgrade.get("current_version"),
            "device_config": system.device_config_name(),
            "internet_connection": self.state.network.get("is_connected"),
            "memory_available": self.state.resource.get("free_memory"),
            "disk_available": self.state.resource.get("available_disk_space"),
            "iot_received_message_count": self.received_message_count,
            "iot_published_message_count": self.published_message_count,
            "recipe_percent_complete": self.state.recipe.get("percent_complete"),
            "recipe_percent_complete_string": recipe_percent_complete_string,
            "recipe_time_remaining_minutes": recipe_time_remaining_minutes,
            "recipe_time_remaining_string": recipe_time_remaining_string,
            "recipe_time_elapsed_string": recipe_time_elapsed_string,
        }

        # Publish summary
        # self.logger.debug("summary = {}".format(summary))
        self.pubsub.publish_command_reply("status", json.dumps(summary))

        # Successfully published summary
        self.logger.debug("Successfully published summary")

    def publish_environmental_variables(self) -> None:
        """Publishes environmental variables."""
        self.logger.debug("Publishing environmental variables")

        # Get environmental variables
        keys = ["reported_sensor_stats", "individual", "instantaneous"]
        environment_variables = accessors.get_nested_dict_safely(
            self.state.environment, keys
        )

        # Ensure environment variables is a dict
        if environment_variables == None:
            environment_variables = {}

        # Keep a copy of the first set of values (usually None). Why?
        if self.prev_environment_variables == {}:
            self.environment_variables = copy.deepcopy(environment_variables)

        # For each value, only publish the ones that have changed.
        for name, value in environment_variables.items():
            if self.prev_environment_variables.get(name) != value:
                self.environment_variables[name] = copy.deepcopy(value)
                self.pubsub.publish_environmenal_variable(name, value)

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

                self.pubsub.publish_binary_image(camera_name, "png", file_bytes)

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
        """Resets iot pubsub. TODO: Should probably be in the pubsub class."""
        try:
            # Pass in the callback that receives commands
            self.pubsub = PubSub(self.state, self.command_received)
        except Exception as e:
            self.pubsub = None
            message = "Unable to reset, unhandled exception".format(type(e))
            self.logger.exception(message)
            self.mode = modes.ERROR

    def publish_message(self, name, msg_json) -> None:
        """Send a command reply. TODO: Not sure where this is used."""
        if self.pubsub is None:
            return
        self.pubsub.publish_command_reply(name, msg_json)

    def command_received(self, command, arg0, arg1):
        """Process commands received from the backend (UI). This is a callback that is 
        called by the IoTPubSub class when this device receives commands from the UI."""

        if self.pubsub == None:
            return

        try:
            if command == commands.START_RECIPE:
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
                self.pubsub.publish_command_reply(command, recipe_json)
                return

            if command == commands.STOP_RECIPE:
                self.recipe.stop_recipe()
                self.pubsub.publish_command_reply(command, "")
                return

            self.logger.error("Received unknown command: {}".format(command))
        except Exception as e:
            message = "Unable to receive command, unhandled exception: {}".format(
                type(e)
            )
            self.logger.message(message)
            return False

    ##### UTILITY-LIKE FUNCTIONS #######################################################

    def _is_registered(self) -> bool:
        """Checks if device is registered."""
        self.logger.debug("Checking if device is registered")

        # Check if file paths exists
        if (
            os.path.exists(DEVICE_ID_PATH)
            and os.path.exists(ROOTS_PATH)
            and os.path.exists(RSA_CERT_PATH)
            and os.path.exists(RSA_PRIVATE_PATH)
        ):
            self.logger.debug("Device is registered")
            return True

        # Device is not registered
        self.logger.debug("Device is not registered")
        return False

    def register(self) -> Optional[str]:
        """Registers device with iot. Returns verification code on success, None on
        failure. TODO: This should re-raise re-named exception instead of returning
        None."""
        self.logger.debug("Registering device")

        # Check network is connected
        if not network.is_connected():
            self.logger.debug("Unable to register, network is not connected")
            return None

        # Build commands
        make_directory_command = ["mkdir", "-p", REGISTRATION_DATA_DIR]
        register_command = [REGISTER_SCRIPT_PATH, REGISTRATION_DATA_DIR]

        # Execute commands
        # Not sure why we delete the verification code...
        try:
            subprocess.run(make_directory_command)
            subprocess.run(register_command)
            verification_code = open(VERIFICATION_CODE_PATH).read()
            os.remove(VERIFICATION_CODE_PATH)
        except Exception as e:
            message = "Unable to register, unhandled exception: {}".format(type(e))
            self.logger.exception(message)
            return None

        # Successfully registered
        message = "Successfully registered, verification code: {}".format(
            verification_code
        )
        self.logger.debug(message)
        return verification_code

    def unregister(self) -> None:
        """Deletes registration data."""
        self.logger.debug("Deleting registration data")

        # TODO: We should probably do this with python functions

        # Build command
        command = ["rm", "-fr", REGISTRATION_DATA_DIR]

        # Execute command
        try:
            with subprocess.run(command):
                self.logger.debug("Successfully deleted iot registration data")
        except Exception as e:
            message = "Unable to delete iot registration data, unhandled exception".format(
                type(e)
            )
            self.logger.exception(message)
