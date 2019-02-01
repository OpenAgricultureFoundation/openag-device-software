# Import standard python modules
import base64, datetime, json, logging, math, os, ssl, sys, time, traceback
import paho.mqtt.client as mqtt

# Import python types
from typing import Dict, Tuple, Optional, Any, NamedTuple, Callable

# Import device utilities
from device.utilities import logger
from device.utilities.state.main import State
from device.utilities.iot import registration, tokens

# Import module elements
from device.iot import commands

# Initialize constants
MQTT_BRIDGE_HOSTNAME = "mqtt.googleapis.com"
MQTT_BRIDGE_PORT = 443

# Initialize message types
COMMAND_REPLY_MESSAGE = "CommandReply"
ENVIRONMENT_VARIABLE_MESSAGE = "EnvVar"
IMAGE_MESSAGE = "Image"
BOOT_MESSAGE = "boot"
STATUS_MESSAGE = "status"

# TODO: Write tests
# TODO: Catch specific exceptions
# TODO: Add static type checking


class PubSub:
    """Handles communication with Google Cloud Platform's Iot Pub/Sub via MQTT."""

    # Initialize state
    is_initialized = False

    def __init__(
        self,
        ref_self: Any,
        on_connect: Callable,
        on_disconnect: Callable,
        on_publish: Callable,
        on_message: Callable,
        on_subscribe: Callable,
        on_log: Callable,
    ) -> None:
        """Initializes pubsub handler."""

        # Initialize parameters
        self.ref_self = ref_self
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.on_publish = on_publish
        self.on_message = on_message
        self.on_subscribe = on_subscribe
        self.on_log = on_log

        # Initialize logger
        self.logger = logger.Logger("PubSub", "iot")

    ##### HELPER FUNCTIONS #############################################################

    def initialize(self) -> None:
        """Initializes pubsub client."""
        self.logger.debug("Initializing")
        try:
            self.load_mqtt_config()
            self.create_mqtt_client()
            self.is_initialized = True
        except Exception as e:
            message = "Unable to initialize, unhandled exception: {}".format(type(e))
            self.logger.exception(message)
            self.is_initialized = False

    def load_mqtt_config(self) -> None:
        """Loads mqtt config."""
        self.logger.debug("Loading mqtt config")

        # Load settings from environment variables
        try:
            self.project_id = os.environ["GCLOUD_PROJECT"]
            self.cloud_region = os.environ["GCLOUD_REGION"]
            self.registry_id = os.environ["GCLOUD_DEV_REG"]
            self.device_id = registration.device_id()
            self.private_key_filepath = os.environ["IOT_PRIVATE_KEY"]
            self.ca_certs = os.environ["CA_CERTS"]
        except KeyError as e:
            message = "Unable to load pubsub config, key {} is required".format(e)
            self.logger.critical(message)
            raise

        # Initialize client id
        self.client_id = "projects/{}/locations/{}/registries/{}/devices/{}".format(
            self.project_id, self.cloud_region, self.registry_id, self.device_id
        )

        # Initialize config topic
        self.config_topic = "/devices/{}/config".format(self.device_id)

        # Initialize event topic
        test_event_topic = os.environ.get("IOT_TEST_TOPIC")
        if test_event_topic is not None:
            self.event_topic = "/devices/{}/{}".format(self.device_id, test_event_topic)
        else:
            self.event_topic = "/devices/{}/events".format(self.device_id)

    def create_mqtt_client(self) -> None:
        """Creates an mqtt client. Returns client and assocaited json web token."""
        self.logger.debug("Creating mqtt client")

        # Initialize client object
        self.client = mqtt.Client(client_id=self.client_id, userdata=self.ref_self)

        # Create json web token
        try:
            self.json_web_token = tokens.create_json_web_token(
                project_id=self.project_id,
                private_key_filepath=self.private_key_filepath,
            )
        except Exception as e:
            message = "Unable to create client, unhandled exception: {}".format(type(e))
            self.logger.exception(message)
            return

        # Pass json web token to google cloud iot core, note username is ignored
        self.client.username_pw_set(
            username="unused", password=self.json_web_token.encoded
        )

        # Enable SSL/TLS support
        self.client.tls_set(ca_certs=self.ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

        # Register message callbacks
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish

        # Connect to the Google MQTT bridge
        self.client.connect(MQTT_BRIDGE_HOSTNAME, MQTT_BRIDGE_PORT)

        # Subscribe to the config topic
        self.client.subscribe(self.config_topic, qos=1)

    def update(self) -> None:
        """Updates pubsub client."""

        # Check if client is initialized
        if not self.is_initialized:
            self.logger.warning(
                "Tried to update before client initialized, initializing client"
            )
            self.initialize()
            return

        # Check if json webtoken is expired, if so renew client
        if self.json_web_token.is_expired:
            self.create_mqtt_client()  # TODO: Renew instead of re-create

        # Update mqtt client
        try:
            self.client.loop()
        except Exception as e:
            message = "Unable to update, unhandled exception: {}".format(type(e))
            self.logger.exception(message)

    ##### PUBLISH FUNCTIONS ############################################################

    def publish_boot_message(self, message: Dict) -> None:
        """Publishes boot message."""
        self.logger.debug("Publishing boot message")

        # Check if client is initialized
        if not self.is_initialized:
            self.logger.warning("Tried to publish before client initialized")
            return

        # Publish message
        message_json = json.dumps(message)
        self.publish_command_reply(BOOT_MESSAGE, message_json)

    def publish_status_message(self, message: Dict) -> None:
        """Publishes status message."""
        self.logger.debug("Publishing status message")

        # Check if client is initialized
        if not self.is_initialized:
            self.logger.warning("Tried to publish before client initialized")
            return

        # Publish message
        message_json = json.dumps(message)
        self.publish_command_reply(STATUS_MESSAGE, message_json)

    ##### PRIVATE PUBLISH FUNCTIONS? ###################################################

    def publish_command_reply(self, command: str, values: str) -> None:
        """Publish a reply to a previously received command. Don't we need the 
        message id then?"""
        self.logger.debug("Publishing command reply")

        # Check if client is initialized
        if not self.is_initialized:
            self.logger.warning("Tried to publish before client initialized")
            return

        # Build message
        message = {
            "messageType": COMMAND_REPLY_MESSAGE, "var": command, "values": values
        }
        message_json = json.dumps(message)

        # Publish message
        try:
            self.client.publish(self.event_topic, message_json, qos=1)
        except Exception as e:
            error_message = "Unable to publish command reply, "
            "unhandled exception: {}".format(type(e))
            self.logger.exception(error_message)

    def publish_environment_variable(
        self, variable_name: str, values_dict: Dict
    ) -> None:
        """Publish a single environment variable."""
        self.logger.debug(
            "Publishing environment variable message: {}".format(variable_name)
        )
        # self.logger.debug("variable_name = {}".format(variable_name))
        # self.logger.debug("values_dict = {}".format(values_dict))

        # Check if client is initialized
        if not self.is_initialized:
            self.logger.warning("Tried to publish message before client initialized")
            return

        # Validate the values
        valid = False
        for vname in values_dict:
            val = values_dict[vname]
            if val is not None:
                valid = True
                break
        if not valid:
            return

        # Build values json
        # TODO: Change this from string manipulation to dict creation then json.dumps
        count = 0
        values_json = "{'values':["
        for vname in values_dict:
            val = values_dict[vname]

            if count > 0:
                values_json += ","
            count += 1

            if isinstance(val, float):
                val = "{0:.2f}".format(val)
                values_json += "{'name':'%s', 'type':'float', 'value':%s}" % (
                    vname, val
                )

            elif isinstance(val, int):
                values_json += "{'name':'%s', 'type':'int', 'value':%s}" % (vname, val)

            else:  # assume str
                values_json += "{'name':'%s', 'type':'str', 'value':'%s'}" % (
                    vname, val
                )
        values_json += "]}"

        # Initialize publish message
        message = {
            "messageType": ENVIRONMENT_VARIABLE_MESSAGE,
            "var": variable_name,
            "values": values_json,
        }

        # Publish message
        try:
            message_json = json.dumps(message)
            self.client.publish(self.event_topic, message_json, qos=1)
        except Exception as e:
            error_message = "Unable to publish environment variables, "
            "unhandled exception: {}".format(type(e))
            self.logger.exception(error_message)

    def publish_binary_image(
        self, variable_name: str, image_type: str, image_bytes: bytes
    ) -> None:
        """Publish a blob as (multiple < 256K) base64 messages. Maximum message size 
        is 256KB, so we may have to send multiple messages,This size is enforced by 
        the Google hosted MQTT server we connect to. See 'Telemetry event payload' 
        https://cloud.google.com/iot/quotas"""
        self.logger.debug("Publishing binary image")

        # Check if client is initialized
        if not self.is_initialized:
            self.logger.warning("Tried to publish before client initialized")
            return

        # Check variable name is valid
        if variable_name == None or len(variable_name) == 0:
            error_message = "Unable to publish binary image, variable name "
            "`{}` is invalid".format(variable_name)
            self.logger.error(error_message)
            raise ValueError(error_message)

        # Check image type is valid
        if image_type == None or image_type == 0:
            error_message = "Unable to publish binary image, image type  "
            "`{}` is invalid".format(image_type)
            self.logger.error(error_message)
            raise ValueError(error_message)

        # Check image bytes are valid
        if image_bytes == None or len(image_bytes) == 0:
            error_message = "Unable to publish binary image, image bytes are invalid"
            self.logger.error(error_message)
            raise ValueError(error_message)

        try:
            # Encode image bytes
            base64_bytes = base64.b64encode(image_bytes)
            max_message_size = 240 * 1024  # < 256K
            image_size = len(base64_bytes)
            total_chunks = math.ceil(image_size / max_message_size)
            image_start_index = 0
            image_end_index = image_size
            if image_size > max_message_size:
                image_end_index = max_message_size

            # Send all messages with the same ID (for tracking and assembly)
            message_id = time.time()

            # make a mutable byte array of the image data
            image_byte_array = bytearray(base64_bytes)

            # break image into messages < 256K
            for chunk in range(0, total_chunks):

                image_chunk = bytes(image_byte_array[image_start_index:image_end_index])

                message = {
                    "messageType": IMAGE_MESSAGE,
                    "messageID": message_id,
                    "varName": variable_name,
                    "imageType": image_type,
                    "chunk": chunk,
                    "totalChunks": total_chunks,
                    "imageChunk": image_chunk.decode("utf-8"),
                }

                # Publish this chunk
                message_json = json.dumps(message)
                self.client.publish(self.event_topic, message_json, qos=1)

                chunk_num_bytes = len(image_chunk.decode("utf-8"))
                # len(message["imageChunk"]
                self.logger.debug(
                    "Publishing binary image, sent image chunk "
                    "{} of {} for {} in {} bytes".format(
                        chunk, total_chunks, variable_name, chunk_num_bytes
                    )
                )

                # For next chunk, start at the ending index
                image_start_index = image_end_index
                image_end_index = image_size  # is this the last chunk?

                # If we have more than one chunk to go, send the max
                if image_size - image_start_index > max_message_size:
                    image_end_index = image_start_index + max_message_size

        except Exception as e:
            error_message = "Unable to publish binary image, unhandled "
            "exception: {}".format(type(e))
            self.logger.exception(error_message)
