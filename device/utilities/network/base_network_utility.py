import socket
import urllib.request
from abc import ABC, abstractmethod

from typing import List, Dict

from device.utilities.logger import Logger


class NetworkUtility(ABC):
    """Abstract class that defines shared and required methods for all concrete NetworkUtility classes"""

    def __init__(self) -> None:
        self.logger = Logger("NetworkUtility", "network")

    def is_connected(self) -> bool:
        """Shared method to determine if the device can reach the network"""
        try:
            urllib.request.urlopen("https://google.com")
            return True
        except urllib.error.URLError as e:  # type: ignore
            self.logger.debug("Network is not connected: {}".format(e))
            return False

    def get_ip_address(self) -> str:
        """Shared method to determine the device's IP address"""
        self.logger.debug("Getting IP Address")

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            return str(s.getsockname()[0])
        except Exception as e:
            message = "Unable to get ip address, unhandled exception: {}".format(
                type(e)
            )
            self.logger.exception(message)
            return "Unknown"

    @abstractmethod
    def get_wifi_ssids(
        self, exclude_hidden: bool = True, exclude_beaglebones: bool = True
    ) -> List[Dict[str, str]]:
        """Abstract method to get wifi SSIDs for configuration"""
        self.logger.debug("Generic Network Util, can't get SSIDs")
        return []

    @abstractmethod
    def join_wifi(self, ssid: str, password: str) -> None:
        """Abstract method to join a wifi network with just a password"""
        self.logger.debug("join_wifi_advance not implemented")
        pass

    @abstractmethod
    def join_wifi_advanced(
        self,
        ssid_name: str,
        passphrase: str,
        hidden_ssid: str,
        security: str,
        eap: str,
        identity: str,
        phase2: str,
    ) -> None:
        """Abstract method to join a wifi network with advanced options"""
        self.logger.debug("join_wifi_advance not implemented")
        pass

    @abstractmethod
    def delete_wifis(self) -> None:
        """Abstract method to forget all known wifi connections"""
        self.logger.debug("delete_wifis not implemented")
        raise SystemError("System does not support deleteing WiFis")
