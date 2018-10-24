# Import standard python modules
import sys, os, subprocess, copy, glob, json, shutil, time, datetime

# Import python types
from typing import Dict, Any, Optional, List, Tuple

# Import device utilities
from device.utilities.statemachine import manager
from device.utilities.state.main import State
from device.utilities import logger, accessors, system, network
from device.utilities import iot as iot_utilities

# Import device managers
from device.recipe.manager import RecipeManager

# Import module elements
from device.iot import modes, commands
from device.iot.pubsub import PubSub

# TODO Notes:
# Add static type checking
# Write tests
# Catch specific exceptions
# Reset IotManager or MQTT / Pubsub connection on network reconnect?
# Run through all state transitions and make sure they are reasonable

# Initialize file paths
IMAGES_DIR = "data/images/"
STORED_IMAGES_DIR = "data/images/stored/"


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

        # Initialize pubsub handler
        self.pubsub = PubSub(
            on_connect=on_connect,
            on_disconnect=on_disconnect,
            on_publish=on_publish,
            on_message=on_message,
            on_subscribe=on_subscribe,
            on_log=on_log,
        )

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

    ##### INTERNAL STATE ACCESS DECORATORS #############################################

    @property
    def is_connected(self) -> False:
        """Gets value."""
        return self.state.iot.get("is_connected", False)  # type: ignore

    @is_connected.setter
    def is_connected(self, value: bool) -> None:
        """Safely updates value in shared state."""
        with self.state.lock:
            self.state.iot["is_connected"] = value

    @property
    def device_id(self) -> str:
        """Gets value."""
        return self.state.iot.get("device_id", "UNKNOWN")  # type: ignore

    @device_id.setter
    def device_id(self, value: boo) -> None:
        """Safely updates value in shared state."""
        with self.state.lock:
            self.state.iot["device_id"] = value

    @property
    def verification_code(self) -> str:
        """Gets value."""
        return self.state.iot.get("verification_code", "UNKNOWN")  # type: ignore

    @verification_code.setter
    def verification_code(self, value: str) -> None:
        """Safely updates value in shared state."""
        with self.state.lock:
            self.state.iot["verification_code"] = value

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

    ##### EXTERNAL STATE ACCESS DECORATORS #############################################

    @property
    def network_is_connected(self) -> bool:
        """Gets value."""
        return self.state.network.get("is_connected", False)  # type: ignore

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
        self.pubsub = PubSub(self.state, self.process_commands)

        # Publish boot message
        self.publish_boot_message()

        # Give othe managers time to initialize. TODO: Can we remove this?
        time.sleep(10)  # seconds

        # Transition to correct registration mode on next state machine update
        if self.is_registered:
            self.mode = modes.REGISTERED
        else:
            self.mode = modes.UNREGISTERED

    def run_unregistered_mode(self) -> None:
        """Runs unregistered mode."""
        self.logger.debug("Entered UNREGISTERED")

        # Loop forever
        while True:

            # Update registration
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

            # Publish system summary, variables, and images every update interval
            if time.time() - last_update_time > update_interval:
                last_update_time = time.time()
                self.publish_system_summary()
                self.publish_environmental_variables()
                self.publish_images()

            # Update pubsub handler
            self.pubsub.update()

            # Check for events
            self.check_events()

            # Check for transitions
            if self.new_transition(modes.REGISTERED):
                break

            # Update every 100ms
            time.sleep(0.1)

    ##### HELPER FUNCTIONS #############################################################

    def update_registration(self) -> None:
        """Updates registration."""

        # Check for network connection
        if not self.network_is_connected:
            return

        # Register device with iot cloud
        try:
            iot_utilities.registration.register()
        except Exception as e:
            message = "Unable to update registration, unhandled exception: {}".format(
                type(e)
            )
            self.logger.exception(message)
            self.mode = modes.ERROR

        # Transition to registered mode on next state machine update
        self.mode = modes.REGISTERED

    ##### IOT PUBLISH FUNCTIONS ########################################################

    def publish_message(self, name, msg_json) -> None:
        """Send a command reply. TODO: Not sure where this is used."""
        if self.pubsub is None:
            return
        self.pubsub.publish_command_reply(name, msg_json)

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
                self.pubsub.publish_environmental_variable(name, value)

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

    ##### DEVICE EVENT FUNCTIONS #######################################################

    def unregister(self) -> Tuple[str, int]:
        """Unregisters device by deleting iot registration data. TODO: This needs to go 
        into the event queue, deleting reg data in middle of a registration update 
        creates an unstable state."""
        self.logger.info("Unregistering device")

        # Delete registration data
        try:
            iot_utilities.registration.delete_data()
        except Exception as e:
            message = "Unable to unregister, unhandled exception: {}".format(type(e))
            self.logger.exception(message)
            self.mode = modes.ERROR
            return message, 500

        # Transition to unregistered mode on next state machine update
        self.mode = modes.UNREGISTERED

        # Successfully deleted registration data
        return "Successfully unregistered device", 200

    #### IOT MESSAGE FUNCTIONS #########################################################

    def process_message(self, message) -> None:
        """Processes messages from iot cloud."""
        self.logger.debug("Processing message")
        self.logger.debug("message type = {}".format(type(message)))
        self.logger.debug("message = {}".format(message))

        # Decode and parse message
        try:
            payload = message.payload.decode("utf-8")
            payload_dict = json.loads(payload)
            message_version = int(payload_dict["lastConfigVersion"])
        except KeyError:
            ref_self.logger.warning("Unable to get message version, setting to 0")
            message_version = 0
        except Exception as e:
            message = "Unable to parse payload, unhandled exception".format(type(e))
            ref_self.logger.exception(message)
            return

        # TODO: Check if message is old

        # Get command messages
        try:
            command_messages = message["commands"]
            message_id = message["messageId"]
        except KeyError as e:
            message = "Unable to get command messages, `{}` key is required".format(e)
            ref_self.logger.error(message)
            return

        # Process a;; command messages
        for command_message in command_messages:
            self.process_command_message(command_message)

    def process_command_message(self, message) -> None:
        """Process commands received from the backend (UI). This is a callback that is 
        called by the IoTPubSub class when this device receives commands from the UI."""
        self.logger.debug("Processing command message")

        # Get command parameters
        try:
            command = message["command"].upper()  # TODO: Fix this, shouldn't need upper
            arg0 = message["arg0"]
            arg1 = message["arg1"]
        except KeyError as e:
            message = "Unable to process command, `{}` key is required".format(e)
            self.logger.error(message)
            return

        # Process command
        if command == commands.START_RECIPE:
            self.forcibly_create_and_start_recipe(command, arg0)
        elif command == commands.STOP_RECIPE:
            self.stop_recipe(command)
        else:
            self.unknown_command(command)

    ##### IOT COMMAND FUNCTIONS ########################################################

    def forcibly_create_and_start_recipe(self, command: str, recipe_json: str) -> None:
        """Forcible starts and creates recipe. TODO: This method should be depricated
        by a cadence of iot commands between iot cloud and this device. Cloud backend
        should look at device state and check if a recipe is already running as well as
        have insight onto what recipes alread exist on the device, etc."""
        self.logger.warning("Forcibly creating and starting recipe")

        # Validate recipe
        is_valid, error = self.recipe.validate(recipe_json)
        if not is_valid:
            self.logger.warning("Received invalid recipe")
            return  # TODO: Return command reply

        # Get recipe uuid
        recipe_dict = json.loads(recipe_json)
        recipe_uuid = recipe_dict["uuid"]

        # Check if recipe already exists on device
        if self.recipe.recipe_exists(recipe_uuid):
            self.logger.warning("Overwriting previously existing recipe")

        # Create or update recipe
        message, status = self.recipe.create_or_update_recipe(recipe_json)

        # Check for create or update recipe errors
        if status != 200:
            message2 = "Unable to create or update recipe, error: {}".format(message)
            self.logger.warning(message2)
            return  # TODO: Return command reply

        # Check if recipe is running, if so stop it
        if self.recipe.is_running:
            self.logger.warning("Forcibly stopping currently running recipe")
            message, status = self.recipe.stop_recipe()

            # Check for stop recipe errors
            if status != 200:
                message2 = "Unable to stop recipe, error: {}".format(message)
                self.logger.warning(message2)
                return  # TODO: Return command reply

        # Start recipe
        message, status = self.recipe.start_recipe(recipe_uuid)

        # Check for start recipe errors
        if status != 200:
            message2 = "Unable to start recipe, error: {}".format(message)
            self.logger.warning(message2)
            return  # TODO: Return command reply

        # Successfully started recipe
        self.pubsub.publish_command_reply(command, recipe_json)

    def stop_recipe(self, command) -> None:
        """Processes stop recipe command."""
        self.logger.debug("Stopping recipe")

        # Stop recipe
        message, status = self.recipe.events.stop_recipe()

        # Check for stop recipe errors
        if status != 200:
            message2 = "Unable to stop recipe, error: {}".format(message)
            self.logger.warning(message2)
            return  # TODO: Return command reply

        # Successfully stopped recipe
        self.pubsub.publish_command_reply(command, "")

    def unknown_command(self, command) -> None:
        """Processes unknown command."""
        self.logger.warning("Received unknown command")
        # TODO: Return command reply


##### PUBSUB CALLBACK FUNCTIONS ########################################################


def on_connect(unused_client, ref_self, unused_flags, rc):
    """Callback for when a device connects to mqtt broker."""
    ref_self.logger.info("Client connected to mqtt broker")
    ref_self.is_connected = True


def on_disconnect(unused_client, ref_self, rc):
    """Callback for when a device disconnects from mqtt broker."""
    error = "{}: {}".format(rc, mqtt.error_string(rc))
    ref_self.logger.info("Client disconnected from mqtt broker, {}".format(error))
    ref_self.is_connected = False


def on_publish(unused_client, ref_self, unused_mid):
    """Callback for when a message is sent to the mqtt broker."""
    ref_self.published_message_count += 1


def on_message(unused_client, ref_self, message) -> None:
    """Callback for when the mqtt broker receives a message on a subscription."""
    ref_self.logger.debug("Received message from broker")

    # Increment received message count
    ref_self.received_message_count += 1

    # Process message
    ref_self.process_message(message)


def on_log(unused_client, ref_self, level, buf):
    """Paho callback when mqtt broker receives a log message."""
    ref_self.logger.debug("Received broker log: '{}' {}".format(buf, level))


def on_subscribe(unused_client, ref_self, mid, granted_qos):
    """Paho callback when mqtt broker receives subscribe."""
    ref_self.logger.debug("Received broker subscribe")
