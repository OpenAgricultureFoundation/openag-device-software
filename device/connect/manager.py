# Import standard python modules
import logging, threading, time, platform

# Import python types
from typing import Dict

# Import device utilities
from device.utilities import logger, accessors, constants
from device.utilities.statemachine import manager, modes
from device.utilities.state.main import State

# Import manager elements
from device.utilities import network as network_utilities

# TODO: Should we rename this to network manager?
# Answer: Depends if we want to interact with iot, e.g. respawn on reconnect
# Or iot manager just watches network manager? or calls network utility?
# Would rather keep seperate unless have a good reason to merge them

# TODO: Should we bring persist ports for port forwarding? Probably want as much of
# the code to live in python land as possible so we don't have to keep track of bash
# scripts and managing crontabs?

# TODO: Should we break out the bash scripts so we're never even calling them, just
# the commands inside of them?


class ConnectManager(manager.StateMachineManager):
    """ Sets up and manages internet and IoT connections. """

    _connected: bool = False

    def __init__(self, state: State) -> None:
        """Initializes connect manager."""

        # Initialize parent class
        super().__init__()

        # Initialize parameters
        self.state = state

        # Initialize logger
        self.logger = logger.Logger("Connect", "connect")
        self.logger.debug("Initializing manager")

        # Initialize reported metrics
        self.status = "Initializing"

        # Initialize state machine transitions
        self.transitions: Dict[str, List[str]] = {
            modes.NORMAL: [modes.SHUTDOWN, modes.ERROR], modes.ERROR: [modes.SHUTDOWN]
        }
        # Initialize state machine mode
        self.mode = modes.NORMAL

    @property
    def internet_is_connected(self) -> bool:
        """Gets internet connection status."""
        return self.state.connect.get("internet_is_connected", False)

    @internet_is_connected.setter
    def internet_is_connected(self, value: bool) -> None:
        """Sets connection status, updates reconnection status, and logs changes."""

        # Set previous and current connection state
        prev_connected = self._connected
        self._connected = value

        # Check for new connection
        if prev_connected != self._connected and self._connected:
            self.logger.info("Connected to internet")
            self.reconnected = True

        # Check for new disconnection
        elif prev_connected != self._connected and not self._connected:
            self.logger.info("Disconnected from internet")
            self.reconnected = False

        # No change to connection
        else:
            self.reconnected = False

        # Update connection status in shared state
        with self.state.lock:
            self.state.resource["internet_is_connected"] = value

    @property
    def wifi_access_points(self) -> bool:
        """Gets value."""
        return self.state.connect.get("wifi_access_points")  # type: ignore

    @wifi_access_points.setter
    def wifi_access_points(self, value: bool) -> None:
        """Safely updates value in shared state."""
        with self.state.lock:
            self.state.connect["wifi_access_points"] = value

    @property
    def ip_address(self) -> bool:
        """Gets value."""
        return self.state.connect.get("ip_address")  # type: ignore

    @ip_address.setter
    def ip_address(self, value: bool) -> None:
        """Safely updates value in shared state."""
        with self.state.lock:
            self.state.connect["ip_address"] = value

    @property
    def remote_device_ui_url(self) -> str:
        """Gets value."""
        return self.state.connect.get("remote_device_ui_url")  # type: ignore

    @remote_device_ui_url.setter
    def remote_device_ui_url(self, value: str) -> None:
        """Safely updates value in shared state."""
        with self.state.lock:
            self.state.connect["remote_device_ui_url"] = value

    # @property
    # def is_bbb(self) -> bool:
    #     """Gets value."""
    #     return self.state.connect.get("is_bbb")  # type: ignore

    # @is_bbb.setter
    # def is_bbb(self, value: bool) -> None:
    #     """Safely updates value in shared state."""
    #     with self.state.lock:
    #         self.state.connect["is_bbb"] = value

    # @property
    # def is_wifi_bbb(self) -> bool:
    #     """Gets value."""
    #     return self.state.connect.get("is_wifi_bbb")  # type: ignore

    # @is_wifi_bbb.setter
    # def is_wifi_bbb(self, value: bool) -> None:
    #     """Safely updates value in shared state."""
    #     with self.state.lock:
    #         self.state.connect["is_wifi_bbb"] = value

    # @property
    # def is_iot_registered(self) -> bool:
    #     """Gets value."""
    #     return self.state.connect.get("is_registered_with_IoT")  # type: ignore

    # @is_iot_registered.setter
    # def is_iot_registered(self, value: bool) -> None:
    #     """Safely updates value in shared state."""
    #     with self.state.lock:
    #         self.state.connect["is_registered_with_IoT"] = value

    # @property
    # def device_id(self) -> str:
    #     """Gets value."""
    #     return self.state.connect.get("device_id")  # type: ignore

    # @device_id.setter
    # def device_id(self, value: str) -> None:
    #     """Safely updates value in shared state."""
    #     with self.state.lock:
    #         self.state.connect["device_id"] = value

    # @property
    # def iot_connection(self) -> bool:
    #     """Gets value."""
    #     return self.state.connect.get("iot_connection")  # type: ignore

    # @iot_connection.setter
    # def iot_connection(self, value: bool) -> None:
    #     """Safely updates value in shared state."""
    #     with self.state.lock:
    #         self.state.connect["iot_connection"] = value

    ##### STATE MACHINE FUNCTIONS ######################################################

    def run(self) -> None:
        """Runs state machine."""

        # Loop forever
        while True:

            # Check if manager is shutdown
            if self.is_shutdown:
                break

            # Check for mode transitions
            if self.mode == modes.NORMAL:
                self.run_normal_mode()
            elif self.mode == modes.ERROR:
                self.run_error_mode()  # defined in parent classs
            elif self.mode == modes.SHUTDOWN:
                self.run_shutdown_mode()  # defined in parent class
            else:
                self.logger.critical("Invalid state machine mode")
                self.mode = modes.INVALID
                self.is_shutdown = True
                break

    def run_normal_mode(self) -> None:
        """Runs normal mode."""

        # Initialize last update time
        last_update_time = 0.0

        # Loop forever
        while True:

            # Set resource update interval
            if not self.internet_is_connected:
                update_interval = 5  # seconds
            else:
                update_interval = 300  # seconds -> 5 minutes

            # Update connection and storage state every update interval
            if time.time() - last_update_time > update_interval:
                last_update_time = time.time()
                self.update_connection()

            # Check for events
            self.check_events()

            # Check for transitions
            if self.new_transition(modes.NORMAL):
                break

            # Update every 100ms
            time.sleep(0.1)

    ##### HELPER FUNCTIONS #############################################################

    def update_connection(self) -> None:
        """Updates connection state."""
        self.internet_is_connected = network_utilities.internet_is_connected()
        self.ip_address = network_utilities.get_ip_address()
        self.wifi_access_points = network_utilities.get_wifi_access_points()

    ##### EVENT FUNCTIONS ##############################################################

    def join_wifi(self, request: Dict[str, Any]) -> Tuple[str, int]:
        """ Joins wifi."""
        self.logger.debug("Joining wifi")

        # Get request parameters
        try:
            wifi_psk = request["wifi_psk"]
            wifi_password = request["wifi_password"]
        except KeyError as e:
            message = "Unable to join wifi, invalid parameter {}".format(e)
            return message, 400

        # Join wifi
        try:
            network_utilities.join_wifi()
        except Exception as e:
            message = "Unable to join wifi, unhandled exception: {}".format(type(e))
            self.logger.exception(message)
            return message, 500

        # Wait for internet connection to be established
        timeout = 5  # seconds
        start_time = time.time()
        while not network_utilities.internet_is_connected():

            # Check for timeout
            if time.time() - start_time > timeout:
                message = "Did not connect to internet within {} ".format(timeout)
                message += "seconds of joining wifi, recheck if internet is connected"
                self.logger.warning(message)
                return message, 202

            # Recheck if internet is connected every second
            time.sleep(1)

        # Succesfully joined wifi
        return "Successfully joined wifi", 200
