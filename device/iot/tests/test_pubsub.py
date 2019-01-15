# Import standard python libraries
import os, sys, pytest, time
import paho.mqtt.client as mqtt

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import device utilities
from device.utilities.state.main import State

# Import device managers
from device.recipe.manager import RecipeManager

# Import manager elements
from device.iot.pubsub import PubSub
from device.iot.manager import IotManager
from device.iot import modes, commands


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


def test_init() -> None:
    state = State()
    recipe = RecipeManager(state)
    iot = IotManager(state, recipe)
    pubsub = PubSub(
        ref_self=iot,
        on_connect=on_connect,
        on_disconnect=on_disconnect,
        on_publish=on_publish,
        on_message=on_message,
        on_subscribe=on_subscribe,
        on_log=on_log,
    )
