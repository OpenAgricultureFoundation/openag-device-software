import socket
import urllib
import os

from typing import List, Dict

from device.utilities.logger import Logger

# Import the subclasses here
from device.utilities.network.generic_network_utility import GenericNetworkUtility
from device.utilities.network.balena_network_utility import BalenaNetworkUtility


class NetworkUtility:

    @staticmethod
    def get_network_utils():
        if os.getenv("BALENA"):  # This is true when running on a Balena enabled platform
            return BalenaNetworkUtility()
        return GenericNetworkUtility()

    def __init__(self):
        self.logger = Logger("NetworkUtility", "network")

    def is_connected(self) -> bool:
        try:
            urllib.request.urlopen("https://google.com")
            return True
        except urllib.error.URLError as e:
            self.logger.debug("Network is not connected: {}".format(e))
            return False

    def get_ip_address(self) -> str:
        self.logger.debug("Getting IP Address")

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            return str(s.getsockname()[0])
        except Exception as e:
            message = "Unable to get ip address, unhandled exception: {}".format(type(e))
            self.logger.exception(message)
            return "Unknown"

    def get_wifi_ssids(self, exclude_hidden: bool = True, exclude_beaglebones: bool = True) -> List[Dict[str, str]]:
        self.logger.debug("Generic Network Util, can't get SSIDs")
        return []

    def join_wifi(self, ssid: str, password: str) -> None:
        self.logger.debug("join_wifi_advance not implemented")
        pass

    def join_wifi_advance(self,
                          ssid_name: str,
                          passphrase: str,
                          hidden_ssid: str,
                          security: str,
                          eap: str,
                          identity: str,
                          phase2: str) -> None:
        self.logger.debug("join_wifi_advance not implemented")
        pass

    def delete_wifis(self) -> None:
        self.logger.debug("delete_wifis not implemented")
        raise SystemError("System does not support deleteing WiFis")