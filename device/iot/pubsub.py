"""
Python3 Class to:
  - Publish data to the Google Cloud IoT Core via MQTT messages.  
  - Subscribe for MQTT config messages which contain commands for the device
    to execute.  The config messages are published by the backend for this
    device.  

JWT (json web tokens) are used for secure device authentication based on RSA
public/private keys. 

After connecting, this process:
 - Publishes data to a common (to all devices) MQTT topic.
 - Subscribes for config messages for only this device specific MQTT topic.
 - Calls the provided callback when commands are received.

rbaynes 2018-09-21
"""


# TODO Notes:
# Remove redundant functions accross connect, iot, update, resource, and upgrade
# We may just want many of these functions in the manager or in device utilities
# Adjust function and variable names to match python conventions
# Add static type checking
# Write tests
# Catch specific exceptions
# Pull out file path strings to top of file
# Inherit from state machine manager
# Always use get method to access dicts unless checking for KeyError (rare cases)
# Always use decorators to access shared state w/state.lock
# Always logger class from device utilities
# Make logic easy to read (descriptive variables, frequent comments, minimized nesting)


# Import standard python modules
import base64, datetime, json, logging, math, os, ssl, sys, time, traceback, jwt
import paho.mqtt.client as mqtt

# Import python types
from typing import Dict, Tuple, Optional, Any, NamedTuple

# Import device utilities
from device.utilities import logger
from device.utilities.state.main import State

# Import app models (TODO: Remove this)
from app.models import IoTConfigModel

# Import app elements
from device.iot import commands


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
        self.logger.debug(self.mqtt_config)
        self.mqtt_client, self.json_web_token = self.create_mqtt_client(
            self.mqtt_config
        )

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
        self.logger.debug("Loaded mqtt config: {}".format(config))
        return config

    def create_mqtt_client(self, config: MQTTConfig) -> Tuple[mqtt.Client, str]:
        """Creates an mqtt client. Returns client and assocaited json web token."""
        self.logger.debug("Creating mqtt client")

        self.logger.debug(config)

        # Initialize client object
        client = mqtt.Client(client_id=config.client_id)

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
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.on_message = self.on_message
        client.on_publish = self.on_publish

        # Connect to the Google MQTT bridge
        client.connect(config.mqtt_bridge_hostname, config.mqtt_bridge_port)

        # Subscribe to the config topic
        client.subscribe(config.config_topic, qos=1)

        # Successfully created mqtt client
        self.logger.debug("Successfully created mqtt client")
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
        issued_timestamp = datetime.datetime.utcnow()
        time_delta = datetime.timedelta(minutes=time_to_live_minutes)
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
        self.logger.debug("Successfully created json web token")
        return json_web_token

    ##### MQTT CALLBACK FUNCTIONS ######################################################

    def on_connect(self, unused_client, unused_flags, rc):
        """Paho callback for when a device connects."""
        self.logger.debug("Called on connect callback")
        # self.logger.debug("on_connect: {}".format(mqtt.connack_string(rc)))
        # ref_self.state["error"] = None

    def on_disconnect(self, unused_client, rc):
        """Paho callback for when a device disconnects."""
        self.logger.debug("Called on disconnect callback")
        # ref_self.connected = False
        # logger.debug("on_disconnect: {}".format(stringify_paho_error(rc)))
        # ref_self.kill_ourselves("IoT disconnected")
        # ref_self.state["error"] = stringify_paho_error(rc)

    def on_publish(self, unused_client, unused_mid):
        """Paho callback when a message is sent to the broker."""
        self.logger.debug("Called on publish function")
        # ref_self.publish_count = ref_self.publish_count + 1
        # logger.debug("on_publish")

    def on_message(self, unused_client, message):
        """Callback when the device receives a message on a subscription."""
        self.logger.debug("Called on message function")

        # ref_self.message_count = ref_self.message_count + 1

        # payload = message.payload.decode("utf-8")
        # # message is a paho.mqtt.client.MQTTMessage, these are all properties:
        # logger.debug(
        #     "Received message:\n  {}\n  topic={}\n  Qos={}\n  "
        #     "mid={}\n  retain={}".format(
        #         payload,
        #         message.topic,
        #         str(message.qos),
        #         str(message.mid),
        #         str(message.retain),
        #     )
        # )

        # # Make sure there is a payload, it could be the first empty config message
        # if len(payload) == 0:
        #     logger.debug("on_message: empty payload.")
        #     return

        # # Convert the payload to a dict and get the last config message version
        # message_version = 0  # starts before the first config version # of 1
        # try:
        #     payload_dict = json.loads(payload)
        #     if "last_config_version" in payload_dict:
        #         message_version = int(payload_dict["last_config_version"])
        # except Exception as e:
        #     logger.debug("on_message: Exception parsing payload: {}".format(e))
        #     return

        # # The broker will keep sending config messages everytime we connect.
        # # So compare this message (if a config message) to the last config
        # # version we have seen.
        # if message_version > ref_self.last_config_version:
        #     ref_self.last_config_version = message_version

        #     # Parse the config message to get the commands in it
        #     ref_self.process_config_message(payload_dict)
        # else:
        #     logger.debug(
        #         "Ignoring this old config message. message_version={} <= last_config_version={}\n".format(
        #             message_version, ref_self.last_config_version
        #         )
        #     )

    def on_log(self, unused_client, level, buf):
        self.logger.debug("Called on log callback")
        # logger.debug("'{}' {}".format(buf, level))

    def on_subscribe(self, unused_client, mid, granted_qos):
        self.logger.debug("Called on subscribe callback")
        # logger.debug("on_subscribe")

    ##### PUBLISH FUNCTIONS ############################################################

    def publish_environmenal_variable(
        self, variable_name: str, values_dict: Dict, message_type: str = "EnvVar"
    ) -> bool:
        """Publish a single environment variable."""
        self.logger.debug("Publishing environment variable: {}".format(variable_name))

        # Check mqtt client exists
        if self.mqtt_client == None:
            message = "Tried to publish environment variable without a valid mqtt client"
            self.logger.warning(message)
            return False

        # Initialize publish message
        message = {}
        message["messageType"] = message_type
        message["var"] = variable_name

        try:
            # command replies only have one value, so make it simple.
            if message_type == "CommandReply":
                message["values"] = values_dict
            else:
                # otherwise this is an env var that could have a list of vals:
                count = 0
                valuesJson = "{'values':["
                for vname in values_dict:
                    val = values_dict[vname]

                    if count > 0:
                        valuesJson += ","
                    count += 1

                    if isinstance(val, float):
                        val = "{0:.2f}".format(val)
                        valuesJson += "{'name':'%s', 'type':'float', 'value':%s}" % (
                            vname, val
                        )

                    elif isinstance(val, int):
                        valuesJson += "{'name':'%s', 'type':'int', 'value':%s}" % (
                            vname, val
                        )

                    else:  # assume str
                        valuesJson += "{'name':'%s', 'type':'str', 'value':'%s'}" % (
                            vname, val
                        )

                valuesJson += "]}"
                message["values"] = valuesJson

            message_json = json.dumps(message)  # dict obj to JSON string

            # Publish the message to the MQTT topic. qos=1 means at least once
            # delivery. Cloud IoT Core also supports qos=0 for at most once
            # delivery.
            self.mqtt_client.publish(self.mqtt_config.event_topic, message_json, qos=1)

        except Exception as e:
            message = "Unable to publish environment variables, unhandled exception: {}".format(
                type(e)
            )
            self.logger.exception(message)
            return False

        # Successfully published environment variables
        message = "Published environment variable payload '{}'' to {}".format(
            message_json, self.mqtt_config.event_topic
        )
        self.logger.debug(message)
        return True

    def publish_command_reply(self, command_name, values_json_string):
        """Publish a reply to a command that was received and successfully processed as 
        an environment variable."""
        try:
            if None == command_name or 0 == len(command_name):
                self.logger.error("publish_command_reply: missing command_name")
                return False

            if None == values_json_string or 0 == len(values_json_string):
                self.logger.error("publish_command_reply: missing values_json_string")
                return False

            # publish the command reply as an env. var.
            self.publish_environmenal_variable(
                variable_name=command_name,
                values_dict=values_json_string,
                message_type="CommandReply",
            )
            return True

        except Exception as e:
            self.logger.critical("publish_command_reply: Exception: %s" % e)
            return False

    def publish_binary_image(self, variable_name, image_type, image_bytes):
        """ Publish a blob as (multiple < 256K) base64 messages. Maximum message size 
        is 256KB, so we may have to send multiple messages,This size is enforced by 
        the Google hosted MQTT server we connect to.
        See 'Telemetry event payload' https://cloud.google.com/iot/quotas"""
        self.logger.debug("Publishing binary image")

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
            self.logger.critical("publish_binary_image: invalid args.")
            return False

        if None == self.mqtt_client:
            return

        try:
            # We send the image as a base64 encoded string (which makes
            # storing message chunks in datastore on the backend easier)

            b64Bytes = base64.b64encode(image_bytes)
            maxMessageSize = 240 * 1024  # < 256K
            imageSize = len(b64Bytes)
            total_chunks = math.ceil(imageSize / maxMessageSize)
            imageStartIndex = 0
            imageEndIndex = imageSize
            if imageSize > maxMessageSize:
                imageEndIndex = maxMessageSize

            # Send all messages with the same ID (for tracking and assembly)
            message_id = time.time()

            # make a mutable byte array of the image data
            imageBA = bytearray(b64Bytes)

            # break image into messages < 256K
            for chunk in range(0, total_chunks):

                image_chunk = bytes(imageBA[imageStartIndex:imageEndIndex])

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
                imageStartIndex = imageEndIndex
                imageEndIndex = imageSize  # is this the last chunk?

                # If we have more than one chunk to go, send the max
                if imageSize - imageStartIndex > maxMessageSize:
                    imageEndIndex = imageStartIndex + maxMessageSize

            return True

        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.logger.critical("publish_binary_image: Exception: {}".format(e))
            traceback.print_tb(exc_traceback, file=sys.stdout)
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
        message = "Command message (id={}): {} {} {}".format(
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

        # Successfully processed command message
        self.logger.debug("Successfully processed command message")

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

        # Successfully processed config message
        self.logger.debug("Successfully processed config message")  # TODO: remove

    def process_network_events(self):
        """Call this function repeatedly from a thread proc or event loop to allow 
        processing of IoT messages."""

        ...

        # try:
        #     # Let the mqtt client process any data it has received or needs to publish
        #     if self.mqtt_client is None:
        #         return
        #     self.mqtt_client.loop()

        #     seconds_since_issue = (datetime.datetime.utcnow() - self.jwt_iat).seconds

        #     # Refresh the JWT if it is about to expire
        #     if seconds_since_issue > 60 * self.jwt_exp_mins:
        #         self.logger.debug(
        #             "Refreshing token after {}s".format(seconds_since_issue)
        #         )
        #         self.jwt_iat = datetime.datetime.utcnow()

        #         # Renew our client with the new token
        #         self.mqtt_client, self.json_web_token = self.create_mqtt_client(
        #             self.mqtt_config
        #         )
        # except Exception as e:
        #     self.logger.critical("Exception processing network events:", e)

    def stringify_paho_error(rc):
        """Convert a Paho error to a human readable string."""
        return "{}: {}".format(rc, mqtt.error_string(rc))
