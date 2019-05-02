# Import standard python modules
import os, copy, glob, json, shutil, time, datetime
import paho.mqtt.client as mqtt

# Import python types
from typing import Dict, Any, List, Tuple

# Import device utilities
from device.utilities.statemachine import manager
from device.utilities.state.main import State
from device.utilities import logger, accessors, system
from device.utilities.iot import registration

# Import device managers
from device.recipe.manager import RecipeManager
from device.recipe import modes as recipe_modes

# Import module elements
from device.iot import modes, commands
from device.iot.pubsub import PubSub

from django.conf import settings

# TODO Notes:
# Write tests
# Catch specific exceptions

# Initialize file paths
DATA_DIR = settings.DATA_PATH

IMAGES_DIR = DATA_DIR + "/images/"
STORED_IMAGES_DIR = DATA_DIR + "/images/stored/"


class IotManager(manager.StateMachineManager):
    """Manages IoT communications to the Google cloud backend MQTT service."""

    # Keep track of the previous values that we have published.
    # We only publish a value if it changes.
    prev_environment_variables: Dict[str, Any] = {}
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
            ref_self=self,
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
                modes.CONNECTED,
                modes.DISCONNECTED,
                modes.ERROR,
                modes.SHUTDOWN,
            ],
            modes.CONNECTED: [
                modes.INIT,
                modes.DISCONNECTED,
                modes.ERROR,
                modes.SHUTDOWN,
            ],
            modes.DISCONNECTED: [
                modes.INIT,
                modes.CONNECTED,
                modes.SHUTDOWN,
                modes.ERROR,
            ],
            modes.ERROR: [modes.SHUTDOWN],
        }

        # Initialize state machine mode
        self.mode = modes.INIT

    ##### INTERNAL STATE DECORATORS ####################################################

    @property
    def is_connected(self) -> bool:
        """Gets value."""
        return self.state.iot.get("is_connected", False)  # type: ignore

    @is_connected.setter
    def is_connected(self, value: bool) -> None:
        """Safely updates value in shared state."""
        with self.state.lock:
            self.state.iot["is_connected"] = value

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
        return self.state.iot.get("device_id", "UNKNOWN")  # type: ignore

    @device_id.setter
    def device_id(self, value: bool) -> None:
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
    def prev_message_id(self) -> str:
        """Gets value."""
        stored = self.state.iot.get("stored", {})
        return stored.get("prev_message_id")  # type: ignore

    @prev_message_id.setter
    def prev_message_id(self, value: str) -> None:
        """Safely updates value in shared state."""
        with self.state.lock:
            if "stored" not in self.state.iot:
                self.state.iot["stored"] = {}
            self.state.iot["stored"]["prev_message_id"] = value

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

    ##### EXTERNAL STATE DECORATORS ####################################################

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
            elif self.mode == modes.CONNECTED:
                self.run_connected_mode()
            elif self.mode == modes.DISCONNECTED:
                self.run_disconnected_mode()
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
        self.pubsub = PubSub(
            self,
            on_connect,
            on_disconnect,
            on_publish,
            on_message,
            on_subscribe,
            on_log,
        )

        # Initialize iot connection state
        self.is_connected = False

        # Initialize registration state
        self.is_registered = registration.is_registered()
        self.device_id = registration.device_id()
        self.verification_code = registration.verification_code()

        # Check if network is connected
        if not self.network_is_connected:
            self.logger.info("Waiting for network to come online")

        # Loop forever
        while True:

            # Check if network is connected
            if self.network_is_connected:
                self.logger.debug("Network came online")
                break

            # Update every 100ms
            time.sleep(0.1)

        # Give the network time to initialize
        time.sleep(30)

        # Check if device is registered
        if not self.is_registered:
            self.logger.debug("Device not registered, registering device")
            registration.register()

            # Update registration state
            self.is_registered = registration.is_registered()
            self.device_id = registration.device_id()
            self.verification_code = registration.verification_code()

        # Initialize pubsub client
        self.pubsub.initialize()

        # Transition to disconnected mode on next state machine update
        self.mode = modes.DISCONNECTED

    def run_disconnected_mode(self) -> None:
        """Runs disconnected mode."""
        self.logger.debug("Entered DISCONNECTED")

        start_time = time.time()
        update_interval = 1  # seconds

        # Loop forever
        while True:

            # Update mqtt broker
            try:
                self.pubsub.update()
            except:
                self.pubsub.initialize()

            # Check if connected, transition if so
            if self.is_connected:
                self.mode = modes.CONNECTED

            # Try to reconnect client every update interval
            if time.time() - start_time > update_interval:
                self.pubsub.client.reconnect()
                start_time = time.time()

            # Check for events
            self.check_events()

            # Check for transitions
            if self.new_transition(modes.DISCONNECTED):
                break

            # Update every 100ms
            time.sleep(0.1)

    def run_connected_mode(self) -> None:
        """Runs connected mode."""
        self.logger.debug("Entered CONNECTED")

        # Publish a boot message
        self.publish_boot_message()

        # Initialize timing variables
        last_update_time = 0.0
        update_interval = 300  # seconds -> 5 minutes

        # Loop forever
        while True:

            # Publish messages
            if time.time() - last_update_time > update_interval:
                last_update_time = time.time()
                self.publish_system_summary()
                self.publish_environment_variables()
                self.publish_images()

            # Update pubsub
            self.pubsub.update()

            # Check for events
            self.check_events()

            # Check for transitions
            if self.new_transition(modes.CONNECTED):
                break

            # Update every 100ms
            time.sleep(0.1)

    ##### IOT PUBLISH FUNCTIONS ###############################################

    def publish_message(self, name: str, message: str) -> None:
        """Send a command reply. TODO: Fix this."""
        self.pubsub.publish_command_reply(name, message)

    def publish_boot_message(self) -> None:
        """Publishes boot message."""
        self.logger.debug("Publishing boot message")

        # Build boot message
        message = {
            "device_config": system.device_config_name(),
            "package_version": self.state.upgrade.get("current_version"),
            "IP": self.state.network.get("ip_address"),
            "access_point": os.getenv("WIFI_ACCESS_POINT"),
            "serial_number": os.getenv("SERIAL_NUMBER"),
            "remote_URL": os.getenv("REMOTE_DEVICE_UI_URL"),
            "bbb_serial": "DEPRECATED",
        }

        # Publish boot message
        self.logger.debug("Boot message: {}".format(message))
        self.pubsub.publish_boot_message(message)

    def publish_system_summary(self) -> None:
        """Publishes status message."""
        self.logger.debug("Publishing system summary")

        # Build summary
        recipe_percent_complete_string = self.state.recipe.get(
            "percent_complete_string"
        )
        recipe_time_remaining_minutes = self.state.recipe.get("time_remaining_minutes")
        recipe_time_remaining_string = self.state.recipe.get("time_remaining_string")
        recipe_time_elapsed_string = self.state.recipe.get("time_elapsed_string")
        message = {
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

        # Publish system summary as a status message
        self.pubsub.publish_status_message(message)

    def publish_environment_variables(self) -> None:
        """Publishes environment variables."""
        self.logger.debug("Publishing environment variables")

        # Get environment variables
        keys = ["reported_sensor_stats", "individual", "instantaneous"]
        environment_variables = accessors.get_nested_dict_safely(
            self.state.environment, keys
        )

        # Ensure environment variables is a dict
        if environment_variables == None:
            environment_variables = {}

        # Keep a copy of the first set of values (usually None). Why?
        #if self.prev_environment_variables == {}:
        #    self.environment_variables = copy.deepcopy(environment_variables)

        # For each value, only publish the ones that have changed.
        for name, value in environment_variables.items():
            if self.prev_environment_variables.get(name) != value:
                self.prev_environment_variables[name] = copy.deepcopy(value)
                self.pubsub.publish_environment_variable(name, value)

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

                # Check the file size
                fsize = os.path.getsize(image_file)
                # If the size is < 200KB, then it is garbage we delete
                # (based on the 1280x1024 average file size)
                if fsize < 500: # in KB
                    os.remove(image_file)
                    continue

                # Upload the image and publish a message it was done
                self.pubsub.upload_image(image_file)

                # Check if stored directory exists, if not create it
                if not os.path.isdir(STORED_IMAGES_DIR):
                    os.mkdir(STORED_IMAGES_DIR)

                # Move image from image directory once processed
                stored_image_file = image_file.replace(IMAGES_DIR, STORED_IMAGES_DIR)
                shutil.move(image_file, stored_image_file)

        except Exception as e:
            message = "Unable to publish images, unhandled exception: {}".format(e)
            self.logger.exception(message)

    ##### DEVICE EVENT FUNCTIONS ##############################################

    def reregister(self) -> Tuple[str, int]:
        """Unregisters device by deleting iot registration data. TODO: This needs to go 
        into the event queue, deleting reg data in middle of a registration update 
        creates an unstable state."""
        self.logger.info("Re-registering device")

        # Check network connection
        if not self.network_is_connected:
            return "Unable to re-register, network disconnected", 400

        # Re-register device and update state
        try:
            registration.delete()
            registration.register()
            self.device_id = registration.device_id()
            self.verification_code = registration.verification_code()
        except Exception as e:
            message = "Unable to re-register, unhandled exception: {}".format(type(e))
            self.logger.exception(message)
            self.mode = modes.ERROR
            return message, 500

        # Transition to init mode on next state machine update
        self.mode = modes.INIT

        # Successfully deleted registration data
        return "Successfully re-registered device", 200

    #### IOT MESSAGE FUNCTIONS #########################################################

    def process_message(self, message: mqtt.MQTTMessage) -> None:
        """Processes messages from iot cloud."""
        self.logger.debug("Processing message")

        # Decode and parse message
        try:
            payload = message.payload.decode("utf-8")
            payload_dict = json.loads(payload)
        except json.decoder.JSONDecodeError:
            self.logger.warning("Unable to process message, payload is invalid json")
            self.logger.warning("payload = `{}`".format(payload))
            return
        except KeyError:
            self.logger.warning("Unable to get message version, setting to 0")
            message_version = 0
        except Exception as e:
            message = "Unable to parse payload, unhandled exception".format(type(e))
            self.logger.exception(message)
            return

        # Get message fields
        try:
            command_messages = payload_dict["commands"]
            message_id = payload_dict["messageId"]
        except KeyError as e:
            message = "Unable to get command messages, `{}` key is required".format(e)
            self.logger.error(message)
            return

        # Check if message is old
        if message_id == self.prev_message_id:
            self.logger.debug("Received old message, not processing")
            return
        else:
            self.prev_message_id = message_id

        # Process all command messages
        for command_message in command_messages:
            self.process_command_message(command_message)

    def process_command_message(self, message: Dict[str, Any]) -> None:
        """Process commands received from the backend (UI). This is a callback that is 
        called by the IoTPubSub class when this device receives commands from the UI."""
        self.logger.debug("Processing command message")

        # Get command parameters
        try:
            command = message["command"].upper()  # TODO: Fix this, shouldn't need upper
            arg0 = message["arg0"]
            arg1 = message["arg1"]
        except KeyError as e:
            error_message = "Unable to process command, `{}` key is required".format(e)
            self.logger.error(error_message)
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
            error_message = "Received invalid recipe"
            self.logger.warning(error_message)
            self.pubsub.publish_command_reply(command, error_message)
            return

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
            error_message = "Unable to create/update recipe, error: {}".format(message)
            self.logger.warning(error_message)
            self.pubsub.publish_command_reply(command, error_message)
            return

        # Check if recipe is active, if so stop it
        if self.recipe.is_active:
            self.logger.warning("Forcibly stopping currently running recipe")
            message, status = self.recipe.stop_recipe()

            # Check for stop recipe errors
            if status != 200:
                error_message = "Unable to stop recipe, error: {}".format(message)
                self.logger.warning(error_message)
                self.pubsub.publish_command_reply(command, error_message)
                return

            # Wait for recipe to stop
            self.logger.debug("Waiting for recipe to stop")

            # Initialize recipe stop timeout parameters
            timeout = 5  # seconds
            start_time = time.time()

            # Loop forever
            while True:

                # Check if recipe manager entered no recipe mode
                if self.recipe.mode == recipe_modes.NORECIPE:
                    self.logger.debug("Recipe successfully stopped")
                    break

                # Check for timeout
                if time.time() - start_time > timeout:
                    error_message = "Unable to start recipe, recipe did not stop within"
                    error_message += " {} seconds of issuing stop command"
                    self.logger.warning(error_message)
                    return

                # Update every 100ms
                time.sleep(0.1)

        # Start recipe
        self.logger.debug("Starting recipe")
        message, status = self.recipe.start_recipe(recipe_uuid)

        # Check for start recipe errors
        if status != 202:
            error_message = "Unable to start recipe, error: {}".format(message)
            self.logger.warning(error_message)

        # Publish command reply
        self.pubsub.publish_command_reply(command, message)

    def stop_recipe(self, command: str) -> None:
        """Processes stop recipe command."""
        self.logger.debug("Stopping recipe")

        # Stop recipe
        message, status = self.recipe.stop_recipe()

        # Check for stop recipe errors
        if status != 200:
            error_message = "Unable to stop recipe, error: {}".format(message)
            self.logger.warning(error_message)

        # Publish command reply
        self.pubsub.publish_command_reply(command, message)

    def unknown_command(self, command: str) -> None:
        """Processes unknown command."""
        message = "Received unknown command"
        self.logger.warning(message)
        self.pubsub.publish_command_reply(command, message)


##### PUBSUB CALLBACK FUNCTIONS ########################################################


def on_connect(
    client: mqtt.Client, ref_self: IotManager, flags: int, return_code: int
) -> None:
    """Callback for when a device connects to mqtt broker."""
    ref_self.is_connected = True


def on_disconnect(client: mqtt.Client, ref_self: IotManager, return_code: int) -> None:
    """Callback for when a device disconnects from mqtt broker."""
    error = "{}: {}".format(return_code, mqtt.error_string(return_code))
    ref_self.is_connected = False


def on_publish(client: mqtt.Client, ref_self: IotManager, message_id: str) -> None:
    """Callback for when a message is sent to the mqtt broker."""
    ref_self.published_message_count += 1


def on_message(
    client: mqtt.Client, ref_self: IotManager, message: mqtt.MQTTMessage
) -> None:
    """Callback for when the mqtt broker receives a message on a subscription."""
    ref_self.logger.debug("Received message from broker")

    # Increment received message count
    ref_self.received_message_count += 1

    # Process message
    ref_self.process_message(message)


def on_log(client: mqtt.Client, ref_self: IotManager, level: str, buf: str) -> None:
    """Paho callback when mqtt broker receives a log message."""
    ref_self.logger.debug("Received broker log: '{}' {}".format(buf, level))


def on_subscribe(
    client: mqtt.Client, ref_self: IotManager, message_id: str, granted_qos: int
) -> None:
    """Paho callback when mqtt broker receives subscribe."""
    ref_self.logger.debug("Received broker subscribe")
