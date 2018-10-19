# Import device utilities
from device.utilities.logger import Logger

# Initialize logger
logger = Logger("MQTT", "iot")


def get_mqtt_client(
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
    logger.debug("client_id={}".format(client_id))

    # The userdata parameter is a reference to our IoTPubSub instance, so
    # callbacks can access the object.encryption_algorithm
    client = mqtt.Client(client_id=client_id, userdata=ref_self)

    # With Google Cloud IoT Core, the username field is ignored, and the
    # password field is used to transmit a JWT to authorize the device.
    client.username_pw_set(
        username="unused",
        password=create_json_web_token(project_id, private_key_file, algorithm),
    )

    # Enable SSL/TLS support.
    client.tls_set(ca_certs=ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

    # Register message callbacks. https://eclipse.org/paho/clients/python/docs/
    # describes additional callbacks that Paho supports.

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_publish = on_publish

    # Connect to the Google MQTT bridge.
    client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

    # This is the topic that the device will receive commands on:
    mqtt_config_topic = "/devices/{}/config".format(device_id)
    logger.debug("mqtt_config_topic={}".format(mqtt_config_topic))

    # Subscribe to the config topic
    client.subscribe(mqtt_config_topic, qos=1)

    return client

    def create_json_web_token(
        self, project_id: str, private_key_filepath: str, algorithm: str
    ):
        """Creates a json web token."""
        self.logger.debug("Creating json web token")

        # Initialize token variables
        issued_time = datetime.datetime.utcnow()
        time_delta = datetime.timedelta(minutes=60)
        expiration_time = issued_time + time_delta

        # Build token
        token = {"iat": issued_time, "exp": expiration_time, "aud": project_id}

        # Load private key
        try:
            with open(private_key_filepath, "r") as f:
                private_key = f.read()
        except Exception as e:
            message = "Unable to create json web token, unhandled exception: {}".format(
                type(e)
            )
            self.logger.exception(message)

        # Encode token
        json_web_token = jwt.encode(token, private_key, algorithm=algorithm)

        # Successfully encoded json web token
        self.logger.debug("Successfully created json web token")
        return json_web_token


def on_connect(unused_client, ref_self, unused_flags, rc):
    """Paho callback for when a device connects."""
    ref_self.connected = True
    logger.debug("on_connect: {}".format(mqtt.connack_string(rc)))
    # ref_self.state["error"] = None


def on_disconnect(unused_client, ref_self, rc):
    """Paho callback for when a device disconnects."""
    ref_self.connected = False
    logger.debug("on_disconnect: {}".format(stringify_paho_error(rc)))
    ref_self.kill_ourselves("IoT disconnected")
    # ref_self.state["error"] = stringify_paho_error(rc)


def on_publish(unused_client, ref_self, unused_mid):
    """Paho callback when a message is sent to the broker."""
    ref_self.publish_count = ref_self.publish_count + 1
    logger.debug("on_publish")


def on_message(unused_client, ref_self, message):
    """Callback when the device receives a message on a subscription."""
    ref_self.message_count = ref_self.message_count + 1

    payload = message.payload.decode("utf-8")
    # message is a paho.mqtt.client.MQTTMessage, these are all properties:
    logger.debug(
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
    if len(payload) == 0:
        logger.debug("on_message: empty payload.")
        return

    # Convert the payload to a dict and get the last config message version
    message_version = 0  # starts before the first config version # of 1
    try:
        payload_dict = json.loads(payload)
        if "last_config_version" in payload_dict:
            message_version = int(payload_dict["last_config_version"])
    except Exception as e:
        logger.debug("on_message: Exception parsing payload: {}".format(e))
        return

    # The broker will keep sending config messages everytime we connect.
    # So compare this message (if a config message) to the last config
    # version we have seen.
    if message_version > ref_self.last_config_version:
        ref_self.last_config_version = message_version

        # Parse the config message to get the commands in it
        ref_self.process_config_message(payload_dict)
    else:
        logger.debug(
            "Ignoring this old config message. message_version={} <= last_config_version={}\n".format(
                message_version, ref_self.last_config_version
            )
        )


def on_log(unused_client, ref_self, level, buf):
    logger.debug("'{}' {}".format(buf, level))


def on_subscribe(unused_client, ref_self, mid, granted_qos):
    logger.debug("on_subscribe")


def stringify_paho_error(rc):
    """Convert a Paho error to a human readable string."""
    return "{}: {}".format(rc, mqtt.error_string(rc))
