# Import standard python modules
import base64, datetime, json, logging, math, os, ssl, sys, time, traceback, jwt
import paho.mqtt.client as mqtt

# Import python types
from typing import Dict, Tuple, Optional, Any, NamedTuple

# Import device utilities
from device.utilities import logger
from device.utilities.state.main import State

# Import app models, TODO: Remove this
from app import models

# Import app elements
from device.iot import commands

# TODO Notes:
# Add static type checking
# Write tests
# Catch specific exceptions


class MQTTConfig(NamedTuple):
    """Dataclass for mqtt config."""
    project_id: str
    cloud_region: str
    registry_id: str
    device_id: str
    client_id: str
    private_key_filepath: str
    ca_certs: str
    config_topic: str
    event_topic: str
    mqtt_bridge_hostname: str = "mqtt.googleapis.com"
    mqtt_bridge_port: int = 443
    jwt_encryption_algorithm: str = "RS256"
    jwt_time_to_live_minutes: int = 60


class JsonWebToken(NamedTuple):
    """Dataclass for json web token."""
    encoded: Any  # TODO: Get type
    issued_timestamp: float
    expiration_timestamp: float


class PubSub:
    """Not really sure what this class does."""

    def __init__(self, state: State, command_received_callback) -> None:
        """Initializes pubsub."""

        # Initialize logger
        self.logger = logger.Logger("PubSub", "iot")
        self.logger.debug("Initializing")

        # Initialize parameters
        self.state = state
        self.command_received_callback = command_received_callback

        # Initialize mqtt client
        self.mqtt_config = self.load_mqtt_config()
        self.mqtt_client, self.json_web_token = self.create_mqtt_client(
            self.mqtt_config
        )

    @property
    def is_connected(self) -> bool:
        """Gets value."""
        return self.state.iot.get("pubsub_is_connected", False)  # type: ignore

    @is_connected.setter
    def is_connected(self, value: bool) -> None:
        """Safely updates value in shared state."""
        with self.state.lock:
            self.state.iot["pubsub_is_connected"] = value

    @property
    def received_message_count(self) -> int:
        """Gets value."""
        return self.state.iot.get("pubsub_received_message_count", 0)  # type: ignore

    @received_message_count.setter
    def received_message_count(self, value: int) -> None:
        """Safely updates value in shared state."""
        with self.state.lock:
            self.state.iot["pubsub_received_message_count"] = value

    @property
    def published_message_count(self) -> int:
        """Gets value."""
        return self.state.iot.get("pubsub_published_message_count", 0)  # type: ignore

    @published_message_count.setter
    def published_message_count(self, value: int) -> None:
        """Safely updates value in shared state."""
        with self.state.lock:
            self.state.iot["pubsub_published_message_count"] = value

    @property
    def last_config_version(self) -> int:
        """Gets value. TODO: Perform this function through stored state."""
        config = models.IoTConfigModel.objects.latest()
        if config != None:
            return config.last_config_version
        else:
            return -1

    @last_config_version.setter
    def last_config_version(self, value: int) -> None:
        """Safely updates value in shared state."""
        models.IoTConfigModel.objects.create(last_config_version=value)

    ##### MQTT FUNCTIONS #############################################################

    def load_mqtt_config(self) -> Optional[MQTTConfig]:
        """Loads mqtt config."""
        self.logger.debug("Loading mqtt config")

        # Load settings from environment variables
        try:
            project_id = os.environ["GCLOUD_PROJECT"]
            cloud_region = os.environ["GCLOUD_REGION"]
            registry_id = os.environ["GCLOUD_DEV_REG"]
            device_id = os.environ["DEVICE_ID"]
            private_key_filepath = os.environ["IOT_PRIVATE_KEY"]
            ca_certs = os.environ["CA_CERTS"]
        except KeyError as e:
            message = "Unable to load iot settings, key `{}` is required".format(e)
            self.logger.critical(message)
            return None

        # Initialize client id
        client_id = "projects/{}/locations/{}/registries/{}/devices/{}".format(
            project_id, cloud_region, registry_id, device_id
        )

        # Initialize config topic
        config_topic = "/devices/{}/config".format(device_id)

        # Initialize event topic
        test_event_topic = os.environ.get("IOT_TEST_TOPIC")
        if test_event_topic is not None:
            event_topic = "/devices/{}/{}".format(device_id, test_event_topic)
        else:
            event_topic = "/devices/{}/events".format(device_id)

        # Build mqtt config object
        config = MQTTConfig(
            project_id=project_id,
            cloud_region=cloud_region,
            registry_id=registry_id,
            device_id=device_id,
            private_key_filepath=private_key_filepath,
            ca_certs=ca_certs,
            client_id=client_id,
            config_topic=config_topic,
            event_topic=event_topic,
        )

        # Successfully loaded mqtt config
        return config

    def create_mqtt_client(self, config: MQTTConfig) -> Tuple[mqtt.Client, str]:
        """Creates an mqtt client. Returns client and assocaited json web token."""
        self.logger.debug("Creating mqtt client")
        # self.logger.debug("config = {}".format(config))

        # Initialize client object
        client = mqtt.Client(client_id=config.client_id, userdata=self)

        # Create json web token
        json_web_token = self.create_json_web_token(
            project_id=config.project_id,
            private_key_filepath=config.private_key_filepath,
            encryption_algorithm=config.jwt_encryption_algorithm,
            time_to_live_minutes=config.jwt_time_to_live_minutes,
        )

        # Pass json web token to google cloud iot core, note username is ignored
        client.username_pw_set(username="unused", password=json_web_token.encoded)

        # Enable SSL/TLS support
        client.tls_set(ca_certs=config.ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

        # Register message callbacks
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_message = on_message
        client.on_publish = on_publish

        # Connect to the Google MQTT bridge
        client.connect(config.mqtt_bridge_hostname, config.mqtt_bridge_port)

        # Subscribe to the config topic
        client.subscribe(config.config_topic, qos=1)

        # Successfully created mqtt client
        return client, json_web_token

    def create_json_web_token(
        self,
        project_id: str,
        private_key_filepath: str,
        encryption_algorithm: str,
        time_to_live_minutes: int,
    ) -> Optional[JsonWebToken]:
        """Creates a json web token."""
        self.logger.debug("Creating json web token")

        # Initialize token variables
        issued_timestamp = datetime.datetime.utcnow().timestamp()
        time_delta = datetime.timedelta(minutes=time_to_live_minutes).seconds
        expiration_timestamp = issued_timestamp + time_delta

        # Build token
        token = {
            "iat": issued_timestamp, "exp": expiration_timestamp, "aud": project_id
        }

        # Load private key
        try:
            with open(private_key_filepath, "r") as f:
                private_key = f.read()
        except Exception as e:
            message = "Unable to create json web token, unable to load private key, unhandled exception: {}".format(
                type(e)
            )
            self.logger.exception(message)
            return None

        # Encode token
        encoded_jwt = jwt.encode(token, private_key, algorithm=encryption_algorithm)

        # Build json web token object
        json_web_token = JsonWebToken(
            encoded=encoded_jwt,
            issued_timestamp=issued_timestamp,
            expiration_timestamp=expiration_timestamp,
        )

        # Successfully encoded json web token
        return json_web_token

    ##### PUBLISH FUNCTIONS ############################################################

    def publish_environmenal_variable(
        self, variable_name: str, values_dict: Dict
    ) -> bool:
        """Publish a single environment variable."""
        self.logger.debug("Publishing environment variable: {}".format(variable_name))

        # Check mqtt client exists
        if self.mqtt_client == None:
            message = "Unable to publish environment variable, non-existant mqtt client"
            self.logger.warning(message)
            return False

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
        message = {"messageType": "EnvVar", "var": variable_name, "values": values_json}

        # Publish message
        try:
            message_json = json.dumps(message)
            self.mqtt_client.publish(self.mqtt_config.event_topic, message_json, qos=1)
        except Exception as e:
            message = "Unable to publish environment variables, unhandled exception: {}".format(
                type(e)
            )
            self.logger.exception(message)
            return False

        # Successfully published environment variables
        return True

    def publish_command_reply(self, command_name: str, values_json_string: str) -> bool:
        """Publish a reply to a command that was received and successfully processed as 
        an environment variable."""
        self.logger.debug("Publishing command reply")

        # Check command name arg is valid
        if command_name == None or len(command_name) == 0:
            message = "Unable to publish command reply, invalid command name"
            self.logger.error(message)
            return False

        # Check values json string is valid
        if values_json_string == None or len(values_json_string) == 0:
            message = "Unable to publish command reply, invalid values json string"
            self.logger.error(message)
            return False

        # Build message payload
        message = {
            "messageType": "CommandReply",
            "var": command_name,
            "values": values_json_string,
        }

        # Publish message payload
        try:
            message_json = json.dumps(message)
            self.mqtt_client.publish(self.mqtt_config.event_topic, message_json, qos=1)
        except Exception as e:
            message = "Unable to publish command reply, unhandled exception: {}".format(
                type(e)
            )
            self.logger.critical(message)
            return False

        # Successfully published command reply
        return True

    def publish_binary_image(
        self, variable_name: str, image_type: str, image_bytes: bytes
    ) -> bool:
        """Publish a blob as (multiple < 256K) base64 messages. Maximum message size 
        is 256KB, so we may have to send multiple messages,This size is enforced by 
        the Google hosted MQTT server we connect to. See 'Telemetry event payload' 
        https://cloud.google.com/iot/quotas"""
        self.logger.debug("Publishing binary image")

        # Check args are valid
        if (
            None == variable_name
            or 0 == len(variable_name)
            or None == image_type
            or 0 == len(image_type)
            or None == image_bytes
            or 0 == len(image_bytes)
            or not isinstance(variable_name, str)
            or not isinstance(image_type, str)
            or not isinstance(image_bytes, bytes)
        ):
            self.logger.error("Unable to publish binary image, invalid args")
            return False

        # Check mqtt client exists
        if None == self.mqtt_client:
            message = "Unable to publish binary image, non-existant mqtt client"
            self.logger.error(message)
            return False

        try:
            # We send the image as a base64 encoded string (which makes
            # storing message chunks in datastore on the backend easier)
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

                message_obj = {}
                message_obj["messageType"] = "Image"
                message_obj["messageID"] = message_id
                message_obj["varName"] = variable_name
                message_obj["imageType"] = image_type
                message_obj["chunk"] = chunk
                message_obj["totalChunks"] = total_chunks
                message_obj["imageChunk"] = image_chunk.decode("utf-8")

                # Publish this chunk
                message_json = json.dumps(message_obj)
                self.mqtt_client.publish(
                    self.mqtt_config.event_topic, message_json, qos=1
                )
                self.logger.info(
                    "publish_binary_image: sent image chunk "
                    "{} of {} for {} in {} bytes".format(
                        chunk,
                        total_chunks,
                        variable_name,
                        len(message_obj["imageChunk"]),
                    )
                )

                # For next chunk, start at the ending index
                image_start_index = image_end_index
                image_end_index = image_size  # is this the last chunk?

                # If we have more than one chunk to go, send the max
                if image_size - image_start_index > max_message_size:
                    image_end_index = image_start_index + max_message_size

            return True

        except Exception as e:
            message = "Unable to publish binary image, unhandled exception: {}".format(
                type(e)
            )
            self.logger.exception(message)
            return False

    ##### MESSAGE PROCESSING FUNCTIONS #################################################

    def process_command_message(self, message: Dict, message_id: str) -> None:
        """Processes a command."""
        self.logger.debug("Processing command message")

        # Parse command message
        try:
            command = message["command"].upper()  # TODO: Fix this, should need upper
            arg0 = message["arg0"]
            arg1 = message["arg1"]
        except KeyError as e:
            message = "Unable to process command, `{}` key is required".format(e)
            self.logger.error(message)
            return

        # Validate command message
        valid_commands = [commands.START_RECIPE, commands.STOP_RECIPE]
        if command not in valid_commands:
            message = "Unable to process command message, `{}` not a valid command".format(
                command
            )
            self.logger.error(message)
            return

        # Command is valid
        message = "Received command message: id={}, cmd={}, arg0={}, arg1={}".format(
            message_id, command, arg0, arg1
        )
        self.logger.debug(message)

        # Run command via callback
        try:
            self.command_received_callback(
                command, arg0, None
            )  # TODO: Why not pass arg1?
        except Exception as e:
            message = "Unable to process command message, unhandled exeption: {}".format(
                type(e)
            )
            self.logger.exception(message)

    def process_config_message(self, message: Dict) -> None:
        """Processes a config message."""
        self.logger.debug("Processing config message")

        # Parse config message
        try:
            command_messages = message["commands"]
            message_id = message["messageId"]
        except KeyError as e:
            message = "Unable to process config message, `{}` key is required".format(e)
            self.logger.error(message)
            return

        # Process command messages
        for command_message in command_messages:
            self.process_command_message(command_message, message_id)

    def process_network_events(self) -> None:
        """Processes network events if new messages exist."""

        # Check if mqtt client exists
        if self.mqtt_client is None:
            return

        try:
            # Let the mqtt client process any data it has received or needs to publish
            self.mqtt_client.loop()

            # Get json web token timing parameters
            current_timestamp = datetime.datetime.utcnow().timestamp()
            issued_timestamp = self.json_web_token.issued_timestamp
            expiration_timestamp = self.json_web_token.expiration_timestamp

            # Refresh the JWT if it is about to expire
            if current_timestamp > expiration_timestamp:
                timestamp_delta = current_timestamp - issued_timestamp
                message = "Refreshing token after {}s".format(timestamp_delta)
                self.logger.debug(message)

                # Renew our client with the new token
                self.mqtt_client, self.json_web_token = self.create_mqtt_client(
                    self.mqtt_config
                )
        except Exception as e:
            message = "Unable to process network events, unhandled exception: {}".format(
                type(e)
            )
            self.logger.exception(message)

    def stringify_paho_error(rc):
        """Convert a Paho error to a human readable string."""
        return "{}: {}".format(rc, mqtt.error_string(rc))


##### CALLBACK FUNCTIONS ###############################################################


def on_connect(unused_client, ref_self, unused_flags, rc):
    """Callback for when a device connects to mqtt broker."""
    ref_self.logger.info("Client connected to mqtt broker")
    ref_self.is_connected = True


def on_disconnect(unused_client, ref_self, rc):
    """Callback for when a device disconnects from mqtt broker."""
    error = stringify_paho_error(rc)
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

    # Decode message
    payload = message.payload.decode("utf-8")

    # Log received message
    ref_self.logger.debug(
        "Received message from broker:  payload={}, topic={}, qos={}, mid={}, retain={}".format(
            payload,
            message.topic,
            str(message.qos),
            str(message.mid),
            str(message.retain),
        )
    )

    # Check payload is not empty
    if len(payload) == 0:
        ref_self.logger.debug("Message broker recieved empty payload")
        return

    # Parse payload
    try:
        payload_dict = json.loads(payload)
        # TODO: Why is the dict key lastConfigVersion and not messageVersion?
        message_version = int(payload_dict.get("lastConfigVersion"))
    except KeyError:
        ref_self.logger.warning("Unable to get message version, setting to 0")
        message_version = 0
    except Exception as e:
        message = "Unable to parse payload, unhandled exception".format(type(e))
        ref_self.logger.exception(message)
        return

    # Check if message is old, broker will send prev config message each time we connect
    prev_version = ref_self.last_config_version
    if message_version < prev_version:
        message = "Ignoring old config message current version: "
        message += "{}, last version: {}".format(message_version, prev_version)

    # Message is new, update config version and parse message
    ref_self.last_config_version = message_version
    ref_self.process_config_message(payload_dict)


def on_log(unused_client, ref_self, level, buf):
    """Paho callback when mqtt broker receives a log message."""
    ref_self.logger.debug("Received broker log: '{}' {}".format(buf, level))


def on_subscribe(unused_client, ref_self, mid, granted_qos):
    """Paho callback when mqtt broker receives subscribe."""
    ref_self.logger.debug("Received broker subscribe")
