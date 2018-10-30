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

import base64, datetime, json, logging, math, os, ssl, sys, time, traceback, jwt
import paho.mqtt.client as mqtt
from app.models import IoTConfigModel


class IoTPubSub:
    """Manages IoT communications to the Google cloud backend MQTT service."""

    # Initialize logging
    extra = {"console_name": "IoT", "file_name": "IoT"}
    logger = logging.getLogger("iot")
    logger = logging.LoggerAdapter(logger, extra)

    # Class constants for parsing received commands
    COMMANDS = "commands"
    message_id = "messageId"
    CMD = "command"
    ARG0 = "arg0"
    ARG1 = "arg1"
    CMD_START = "START_RECIPE"
    CMD_STOP = "STOP_RECIPE"
    # CMD_STATUS  = 'STATUS'
    # CMD_NOOP    = 'NOOP'
    # CMD_RESET   = 'RESET'

    # Class member vars
    _lastConfigVersion = 0  # The last config message version we have seen.
    _connected = False  # Property
    _messageCount = 0  # Property
    _publishCount = 0  # Property
    deviceId = None  # Our device ID.
    mqtt_topic = None  # PubSub topic we publish to.
    jwt_iat = 0
    jwt_exp_mins = 0
    mqtt_client = None
    logNumericLevel = logging.ERROR  # default
    encryptionAlgorithm = "RS256"  # for JWT (RSA 256 bit)
    args = None  # Class configuration

    def __init__(self, ref_iot_manager, command_received_callback, state_dict):
        """ Initialized IoT manager."""
        self.ref_iot_manager = ref_iot_manager
        self.command_received_callback = command_received_callback
        self.state_dict = state_dict  # items that are shown in the UI
        self.args = self.get_env_vars()  # get our settings from env. vars.
        self.deviceId = self.args.device_id

        # Read our IoT config settings from the DB (if they exist).
        try:
            c = IoTConfigModel.objects.latest()
            self._lastConfigVersion = c.last_config_version
        except:
            # Or create a DB entry since none exists.
            IoTConfigModel.objects.create(last_config_version=self._lastConfigVersion)

        # Validate our deviceId
        if self.deviceId is None or 0 == len(self.deviceId):
            msg = "Invalid or missing DEVICE_ID env. var."
            self.kill_ourselves(msg)

        self.logger.debug("Using device_id={}".format(self.deviceId))

        # The MQTT events topic we publish messages to
        self.mqtt_topic = "/devices/{}/events".format(self.deviceId)

        # if we are running a test client to publish to a test topic,
        # then change the above variable.  (this requires a MQTT server -
        # usally a local developer instance) to be running and listening
        # on this same topic (device-test/test).
        test_topic = os.environ.get("IOT_TEST_TOPIC")
        if test_topic is not None:
            self.mqtt_topic = "/devices/{}/{}".format(self.deviceId, test_topic)

        self.logger.debug("mqtt_topic={}".format(self.mqtt_topic))

        # Create a (renewable) client with tokens that will timeout
        # Let any exceptions pass for this (no internet conn)
        self.jwt_iat = datetime.datetime.utcnow()
        self.jwt_exp_mins = self.args.jwt_expires_minutes
        self.mqtt_client = get_mqtt_client(
            self,
            self.args.project_id,
            self.args.cloud_region,
            self.args.registry_id,
            self.deviceId,
            self.args.private_key_file,
            self.encryptionAlgorithm,
            self.args.ca_certs,
            self.args.mqtt_bridge_hostname,
            self.args.mqtt_bridge_port,
        )

    def kill_ourselves(self, msg):
        """Used by the phao callbacks if we need to tell the manager to recreate us."""

        self.state_dict["connected"] = "No"
        self.ref_iot_manager.kill_iot_pubsub(msg)

    def publish_env_var(self, var_name, values_dict, message_type="EnvVar"):
        """Publish a single environment variable."""
        try:
            if None == self.mqtt_client:
                return
            message_obj = {}
            message_obj["messageType"] = message_type
            message_obj["var"] = var_name

            # command replies only have one value, so make it simple.
            if message_type == "CommandReply":
                message_obj["values"] = values_dict
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
                            vname,
                            val,
                        )

                    elif isinstance(val, int):
                        valuesJson += "{'name':'%s', 'type':'int', 'value':%s}" % (
                            vname,
                            val,
                        )

                    else:  # assume str
                        valuesJson += "{'name':'%s', 'type':'str', 'value':'%s'}" % (
                            vname,
                            val,
                        )

                valuesJson += "]}"
                message_obj["values"] = valuesJson

            message_json = json.dumps(message_obj)  # dict obj to JSON string

            # Publish the message to the MQTT topic. qos=1 means at least once
            # delivery. Cloud IoT Core also supports qos=0 for at most once
            # delivery.
            self.mqtt_client.publish(self.mqtt_topic, message_json, qos=1)

            self.logger.info(
                "publish_env_var: sent '{}' to {}".format(message_json, self.mqtt_topic)
            )
            return True

        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.logger.critical("publish_env_var: Exception: {}".format(e))
            traceback.print_tb(exc_traceback, file=sys.stdout)
            return False

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
            self.publish_env_var(
                var_name=command_name,
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

                msg_obj = {}
                msg_obj["messageType"] = "Image"
                msg_obj["messageID"] = message_id
                msg_obj["varName"] = variable_name
                msg_obj["imageType"] = image_type
                msg_obj["chunk"] = chunk
                msg_obj["totalChunks"] = total_chunks
                msg_obj["imageChunk"] = image_chunk.decode("utf-8")

                # Publish this chunk
                msg_json = json.dumps(msg_obj)
                self.mqtt_client.publish(self.mqtt_topic, msg_json, qos=1)
                self.logger.info(
                    "publish_binary_image: sent image chunk "
                    "{} of {} for {} in {} bytes".format(
                        chunk, total_chunks, variable_name, len(msg_obj["imageChunk"])
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

    def process_network_events(self):
        """Call this function repeatedly from a thread proc or event loop to allow 
        processing of IoT messages."""
        try:
            # Let the mqtt client process any data it has received or needs to publish
            if self.mqtt_client is None:
                return
            self.mqtt_client.loop()

            seconds_since_issue = (datetime.datetime.utcnow() - self.jwt_iat).seconds

            # Refresh the JWT if it is about to expire
            if seconds_since_issue > 60 * self.jwt_exp_mins:
                self.logger.debug(
                    "Refreshing token after {}s".format(seconds_since_issue)
                )
                self.jwt_iat = datetime.datetime.utcnow()

                # Renew our client with the new token
                self.mqtt_client = get_mqtt_client(
                    self,
                    self.args.project_id,
                    self.args.cloud_region,
                    self.args.registry_id,
                    self.deviceId,
                    self.args.private_key_file,
                    self.encryptionAlgorithm,
                    self.args.ca_certs,
                    self.args.mqtt_bridge_hostname,
                    self.args.mqtt_bridge_port,
                )
        except (Exception) as e:
            self.logger.critical("Exception processing network events:", e)

    @property
    def lastConfigVersion(self):
        """Get the last version of a config message (command) we received."""
        return self._lastConfigVersion

    @lastConfigVersion.setter
    def lastConfigVersion(self, value):
        """Save the last version of a config message (command) we received."""
        self._lastConfigVersion = value
        try:
            c = IoTConfigModel.objects.latest()
            c.last_config_version = value
            c.save()
        except:
            IoTConfigModel.objects.create(last_config_version=value)

    @property
    def connected(self):
        return self._connected

    @connected.setter
    def connected(self, value):
        self._connected = value
        if value:
            self.state_dict["connected"] = datetime.datetime.utcnow().strftime(
                "%Y-%m-%d-T%H:%M:%SZ"
            )
        else:
            self.state_dict["connected"] = "No"

    @property
    def messageCount(self):
        return self._messageCount

    @messageCount.setter
    def messageCount(self, value):
        self._messageCount = value
        self.state_dict["received_message_count"] = value

    @property
    def publishCount(self):
        return self._publishCount

    @publishCount.setter
    def publishCount(self, value):
        self._publishCount = value
        self.state_dict["published_message_count"] = value

    ####################################################################
    # Private internal classes / methods below here.  Don't call them. #
    ####################################################################

    class IoTArgs:
        """Class arguments with defaults."""

        project_id = None
        registry_id = None
        device_id = None
        private_key_file = None
        cloud_region = None
        ca_certs = None
        mqtt_bridge_hostname = "mqtt.googleapis.com"
        mqtt_bridge_port = 443  # clould also be 8883
        jwt_expires_minutes = 20

    def get_env_vars(self):
        """Gets our IoT settings from environment variables and defaults, sets our 
        logger level. Returns an IoTArgs."""
        args = self.IoTArgs()

        args.project_id = os.environ.get("GCLOUD_PROJECT")
        if args.project_id is None:
            msg = "iot_pubsub: get_env_vars: " "Missing GCLOUD_PROJECT environment variable."
            self.kill_ourselves(msg)

        args.cloud_region = os.environ.get("GCLOUD_REGION")
        if args.cloud_region is None:
            msg = "iot_pubsub: get_env_vars: " "Missing GCLOUD_REGION environment variable."
            self.kill_ourselves(msg)

        args.registry_id = os.environ.get("GCLOUD_DEV_REG")
        if args.registry_id is None:
            msg = "iot_pubsub: get_env_vars: " "Missing GCLOUD_DEV_REG environment variable."
            self.kill_ourselves(msg)

        args.device_id = os.environ.get("DEVICE_ID")
        if args.device_id is None:
            msg = "iot_pubsub: get_env_vars: " "Missing DEVICE_ID environment variable."
            self.kill_ourselves(msg)

        args.private_key_file = os.environ.get("IOT_PRIVATE_KEY")
        if args.private_key_file is None:
            msg = "iot_pubsub: get_env_vars: " "Missing IOT_PRIVATE_KEY environment variable."
            self.kill_ourselves(msg)

        args.ca_certs = os.environ.get("CA_CERTS")
        if args.ca_certs is None:
            msg = "iot_pubsub: get_env_vars: " "Missing CA_CERTS environment variable."
            self.kill_ourselves(msg)

        return args

    def parse_command(self, d, message_id):
        """Parse the single command message.Returns True or False."""
        try:
            # validate keys
            if not valid_dict_key(d, self.CMD):
                self.logger.error("Message is missing %s key." % self.CMD)
                return False
            if not valid_dict_key(d, self.ARG0):
                self.logger.error("Message is missing %s key." % self.ARG0)
                return False
            if not valid_dict_key(d, self.ARG1):
                self.logger.error("Message is missing %s key." % self.ARG1)
                return False

            # validate the command
            commands = [self.CMD_START, self.CMD_STOP]
            cmd = d[self.CMD].upper()  # compare string command in upper case
            if cmd not in commands:
                self.logger.error("%s is not a valid command." % d[self.CMD])
                return False

            self.logger.debug(
                "Received command message_id=%s %s %s %s"
                % (message_id, d[self.CMD], d[self.ARG0], d[self.ARG1])
            )

            # write the binary brain command to the FIFO
            # (the brain will validate the args)
            if cmd == self.CMD_START or cmd == self.CMD_STOP:
                # arg0: JSON recipe string (for start, nothing for stop)
                self.logger.info("Command: %s" % cmd)
                self.command_received_callback(cmd, d[self.ARG0], None)
                return True

        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.logger.critical("Exception in parse_command(): %s" % e)
            traceback.print_tb(exc_traceback, file=sys.stdout)
            return False

    def parse_config_message(self, d):
        """Parse the config messages we receive.
        Arg 'd': dict created from the data received with the config MQTT message."""
        try:
            if not valid_dict_key(d, self.COMMANDS):
                self.logger.error("Message is missing %s key." % self.COMMANDS)
                return

            if not valid_dict_key(d, self.message_id):
                self.logger.error("Message is missing %s key." % self.message_id)
                return

            # unpack an array of commands from the dict
            for cmd in d[self.COMMANDS]:
                self.parse_command(cmd, d[self.message_id])

        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.logger.critical("Exception in parse_config_message(): %s" % e)
            traceback.print_tb(exc_traceback, file=sys.stdout)


##########################################################
# Private internal methods below here.  Don't call them. #
##########################################################

# --------------------------------------------------------------------------
# private
"""
Creates a JWT (https://jwt.io) to establish an MQTT connection.
Args:
    project_id: The cloud project ID this device belongs to
    private_key_file: A path to a file containing an RSA256 private key.
    algorithm: The encryption algorithm to use: 'RS256'.
Returns:
    An MQTT generated from the given project_id and private key, which
    expires in 20 minutes. After 20 minutes, your client will be
    disconnected, and a new JWT will have to be generated.
Raises:
    ValueError: If the private_key_file does not contain a known key.
"""


def create_jwt(ref_self, project_id, private_key_file, algorithm):
    token = {
        # The time that the token was issued at
        "iat": datetime.datetime.utcnow(),
        # The time the token expires.
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        # The audience field should always be set to the GCP project id.
        "aud": project_id,
    }

    # Read the private key file.
    with open(private_key_file, "r") as f:
        private_key = f.read()

    ref_self.logger.debug(
        "Creating JWT using {} from private key file {}".format(
            algorithm, private_key_file
        )
    )

    return jwt.encode(token, private_key, algorithm=algorithm)


def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return "{}: {}".format(rc, mqtt.error_string(rc))


def on_connect(unused_client, ref_self, unused_flags, rc):
    """Paho callback for when a device connects."""
    ref_self.connected = True
    ref_self.logger.debug("on_connect: {}".format(mqtt.connack_string(rc)))
    ref_self.state_dict["error"] = None


def on_disconnect(unused_client, ref_self, rc):
    """Paho callback for when a device disconnects."""
    ref_self.connected = False
    ref_self.logger.debug("on_disconnect: {}".format(error_str(rc)))
    ref_self.state_dict["error"] = error_str(rc)
    ref_self.kill_ourselves("IoT disconnected")


def on_publish(unused_client, ref_self, unused_mid):
    """Paho callback when a message is sent to the broker."""
    ref_self.publishCount = ref_self.publishCount + 1
    ref_self.logger.debug("on_publish")


def on_message(unused_client, ref_self, message):
    """Callback when the device receives a message on a subscription."""
    ref_self.messageCount = ref_self.messageCount + 1

    payload = message.payload.decode("utf-8")
    # message is a paho.mqtt.client.MQTTMessage, these are all properties:
    ref_self.logger.debug(
        "Received message:\n  {}\n  topic={}\n  Qos={}\n  "
        "mid={}\n  retain={}".format(
            payload,
            message.topic,
            str(message.qos),
            str(message.mid),
            str(message.retain),
        )
    )

    # Make sure there is a payload, it could be the first empty config message
    if 0 == len(payload):
        ref_self.logger.debug("on_message: empty payload.")
        return

    # Convert the payload to a dict and get the last config msg version
    messageVersion = 0  # starts before the first config version # of 1
    try:
        payload_dict = json.loads(payload)
        if "lastConfigVersion" in payload_dict:
            messageVersion = int(payload_dict["lastConfigVersion"])
    except Exception as e:
        ref_self.logger.debug("on_message: Exception parsing payload: {}".format(e))
        return

    # The broker will keep sending config messages everytime we connect.
    # So compare this message (if a config message) to the last config
    # version we have seen.
    if messageVersion > ref_self.lastConfigVersion:
        ref_self.lastConfigVersion = messageVersion

        # Parse the config message to get the commands in it
        ref_self.parse_config_message(payload_dict)
    else:
        ref_self.logger.debug(
            "Ignoring this old config message. messageVersion={} <= lastConfigVersion={}\n".format(
                messageVersion, ref_self.lastConfigVersion
            )
        )


def on_log(unused_client, ref_self, level, buf):
    ref_self.logger.debug("'{}' {}".format(buf, level))


def on_subscribe(unused_client, ref_self, mid, granted_qos):
    ref_self.logger.debug("on_subscribe")


def get_mqtt_client(
    ref_self,
    project_id,
    cloud_region,
    registry_id,
    device_id,
    private_key_file,
    algorithm,
    ca_certs,
    mqtt_bridge_hostname,
    mqtt_bridge_port,
):
    """Create our MQTT client. The client_id is a unique string that identifies
    this device. For Google Cloud IoT Core, it must be in the format below."""

    # projects/openag-v1/locations/us-central1/registries/device-registry/devices/my-python-device
    client_id = "projects/{}/locations/{}/registries/{}/devices/{}".format(
        project_id, cloud_region, registry_id, device_id
    )
    ref_self.logger.debug("client_id={}".format(client_id))

    # The userdata parameter is a reference to our IoTPubSub instance, so
    # callbacks can access the object.
    client = mqtt.Client(client_id=client_id, userdata=ref_self)

    # With Google Cloud IoT Core, the username field is ignored, and the
    # password field is used to transmit a JWT to authorize the device.
    client.username_pw_set(
        username="unused",
        password=create_jwt(ref_self, project_id, private_key_file, algorithm),
    )

    # Enable SSL/TLS support.
    client.tls_set(ca_certs=ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

    # Register message callbacks. https://eclipse.org/paho/clients/python/docs/
    # describes additional callbacks that Paho supports.
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_publish = on_publish
    # client.on_subscribe = on_subscribe     # only for debugging
    # client.on_log = on_log                 # only for debugging

    # Connect to the Google MQTT bridge.
    client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

    # This is the topic that the device will receive COMMANDS on:
    mqtt_config_topic = "/devices/{}/config".format(device_id)
    ref_self.logger.debug("mqtt_config_topic={}".format(mqtt_config_topic))

    # Subscribe to the config topic.
    client.subscribe(mqtt_config_topic, qos=1)

    return client


def valid_dict_key(d, key):
    """Utility function to check if a key is in a dict."""
    if key in d:
        return True
    else:
        return False
