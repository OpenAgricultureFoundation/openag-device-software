# Import standard python modules
import logging, threading, time, platform

# Import python types
from typing import Dict, Any, Tuple, List

# Import device utilities
from device.utilities import logger, accessors, constants
from device.utilities.statemachine import manager
from device.utilities.state.main import State
from device.utilities import network as network_utilities

# Import manager elements
from device.network import modes

# TODO: Should we bring persist ports for port forwarding? Probably want as much of
# the code to live in python land as possible so we don't have to keep track of bash
# scripts?

# TODO: Should we break out the bash scripts so we're never even calling them, just
# the commands inside of them?


class NetworkManager(manager.StateMachineManager):
    """Manages network connections."""

    _connected: bool = False

    def __init__(self, state: State) -> None:
        """Initializes network manager."""

        # Initialize parent class
        super().__init__()

        # Initialize parameters
        self.state = state

        # Initialize logger
        self.logger = logger.Logger("NetworkManager", "network")
        self.logger.debug("Initializing manager")

        # Initialize reported metrics
        self.status = "Initializing"

        # Initialize state machine transitions
        self.transitions: Dict[str, List[str]] = {
            modes.CONNECTED: [modes.DISCONNECTED, modes.SHUTDOWN, modes.ERROR],
            modes.DISCONNECTED: [modes.CONNECTED, modes.SHUTDOWN, modes.ERROR],
            modes.ERROR: [modes.SHUTDOWN],
        }

        # Initialize state machine mode
        self.mode = modes.DISCONNECTED

    @property
    def is_connected(self) -> bool:
        """Gets internet connection status."""
        return self.state.network.get("is_connected", False)

    @is_connected.setter
    def is_connected(self, value: bool) -> None:
        """Sets connection status, updates reconnection status, and logs changes."""

        # Set previous and current connection state
        prev_connected = self._connected
        self._connected = value

        # Check for new connection
        if prev_connected != self._connected and self._connected:
            self.logger.info("Connected to internet")
            self.reconnected = True
            self.mode = modes.CONNECTED

        # Check for new disconnection
        elif prev_connected != self._connected and not self._connected:
            self.logger.info("Disconnected from internet")
            self.reconnected = False
            self.mode = modes.DISCONNECTED

        # No change to connection
        else:
            self.reconnected = False

        # Update connection status in shared state
        with self.state.lock:
            self.state.network["is_connected"] = value

    @property
    def wifi_access_points(self) -> List[Dict[str, str]]:
        """Gets value."""
        return self.state.network.get("wifi_access_points")  # type: ignore

    @wifi_access_points.setter
    def wifi_access_points(self, value: List[Dict[str, str]]) -> None:
        """Safely updates value in shared state."""
        with self.state.lock:
            self.state.network["wifi_access_points"] = value

    @property
    def ip_address(self) -> str:
        """Gets value."""
        return self.state.network.get("ip_address")  # type: ignore

    @ip_address.setter
    def ip_address(self, value: str) -> None:
        """Safely updates value in shared state."""
        with self.state.lock:
            self.state.network["ip_address"] = value

    ##### STATE MACHINE FUNCTIONS ######################################################

    def run(self) -> None:
        """Runs state machine."""

        # Loop forever
        while True:

            # Check if manager is shutdown
            if self.is_shutdown:
                break

            # Check for mode transitions
            if self.mode == modes.CONNECTED:
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

    def run_connected_mode(self) -> None:
        """Runs normal mode."""
        self.logger.debug("Entered CONNECTED")

        # Initialize timing variables
        last_update_time = 0.0
        update_interval = 300  # seconds -> 5 minutes

        # Loop forever
        while True:

            # Update connection and storage state every update interval
            if time.time() - last_update_time > update_interval:
                last_update_time = time.time()
                self.update_connection()

            # Check for network disconnect
            if not self.is_connected:
                self.mode = modes.DISCONNECTED

            # Check for events
            self.check_events()

            # Check for transitions
            if self.new_transition(modes.CONNECTED):
                break

            # Update every 100ms
            time.sleep(0.1)

    def run_disconnected_mode(self) -> None:
        """Runs normal mode."""
        self.logger.debug("Entered DISCONNECTED")

        # Initialize timing variables
        last_update_time = 0.0
        update_interval = 5  # seconds

        # Loop forever
        while True:

            # Update connection and storage state every update interval
            if time.time() - last_update_time > update_interval:
                last_update_time = time.time()
                self.update_connection()

            # Check for network connect
            if self.is_connected:
                self.mode = modes.CONNECTED

            # Check for events
            self.check_events()

            # Check for transitions
            if self.new_transition(modes.DISCONNECTED):
                break

            # Update every 100ms
            time.sleep(0.1)

    ##### HELPER FUNCTIONS #############################################################

    def update_connection(self) -> None:
        """Updates connection state."""
        self.is_connected = network_utilities.is_connected()
        if self.is_connected:
            self.ip_address = network_utilities.get_ip_address()
        else:
            self.ip_address = "UNKNOWN"

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
        self.logger.debug("Sending join wifi request")
        try:
            network_utilities.join_wifi(wifi_psk, wifi_password)
        except Exception as e:
            message = "Unable to join wifi, unhandled exception: {}".format(type(e))
            self.logger.exception(message)
            return message, 500

        # Wait for internet connection to be established
        timeout = 60  # seconds
        start_time = time.time()
        while not network_utilities.is_connected():
            self.logger.debug("Waiting for network connection")

            # Check for timeout
            if time.time() - start_time > timeout:
                message = "Did not connect to internet within {} ".format(timeout)
                message += "seconds of joining wifi, recheck if internet is connected"
                self.logger.warning(message)
                return message, 202

            # Recheck if internet is connected every second
            time.sleep(2)

        # Update connection state
        self.is_connected = True

        # Succesfully joined wifi
        self.logger.debug("Successfully joined wifi")
        return "Successfully joined wifi", 200

    def join_wifi_advanced(self, request: Dict[str, Any]) -> Tuple[str, int]:
        """ Joins wifi."""
        self.logger.debug("Joining wifi advanced")

        # Get request parameters
        try:
            ssid_name = request["ssid_name"]
            passphrase = request["passphrase"]
            hidden_ssid = request["hidden_ssid"]
            security = request["security"]
            eap = request["eap"]
            identity = request["identity"]
            phase2 = request["phase2"]
        except KeyError as e:
            message = "Unable to join wifi advanced, invalid parameter `{}`".format(e)
            return message, 400

        # Join wifi advanced
        self.logger.debug("Sending join wifi request to network utility")
        try:
            network_utilities.join_wifi_advanced(
                ssid_name, passphrase, hidden_ssid, security, eap, identity, phase2
            )
        except Exception as e:
            message = "Unable to join wifi advanced, unhandled exception: {}".format(
                type(e)
            )
            self.logger.exception(message)
            return message, 500

        # Wait for internet connection to be established
        timeout = 60  # seconds
        start_time = time.time()
        while not network_utilities.is_connected():
            self.logger.debug("Waiting for network to connect")

            # Check for timeout
            if time.time() - start_time > timeout:
                message = "Did not connect to internet within {} ".format(timeout)
                message += "seconds of joining wifi, recheck if internet is connected"
                self.logger.warning(message)
                return message, 202

            # Recheck if internet is connected every second
            time.sleep(2)

        # Update connection state
        self.is_connected = True

        # Succesfully joined wifi advanced
        self.logger.debug("Successfully joined wifi advanced")
        return "Successfully joined wifi advanced", 200

    def delete_wifis(self) -> Tuple[str, int]:
        """ Deletes wifi."""
        self.logger.debug("Deleting wifis")

        # Join wifi
        try:
            network_utilities.delete_wifis()
        except Exception as e:
            message = "Unable to delete wifi, unhandled exception: {}".format(type(e))
            self.logger.exception(message)
            return message, 500

        # Wait for internet to be disconnected
        timeout = 10  # seconds
        start_time = time.time()
        while network_utilities.is_connected():
            self.logger.debug("Waiting for internet to disconnect")

            # Check for timeout
            if time.time() - start_time > timeout:
                message = "Did not disconnect from internet within {} ".format(timeout)
                message += "seconds of deleting wifis"
                self.logger.warning(message)
                return message, 202

            # Recheck if internet is connected every second
            time.sleep(2)

        # Update connection state
        self.is_connected = False

        # Succesfully deleted wifi
        self.logger.debug("Successfully deleted wifis")
        return "Successfully deleted wifis", 200
