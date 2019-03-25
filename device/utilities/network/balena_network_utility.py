import subprocess
from pathlib import Path
from typing import List, Dict
from django.conf import settings
import os

from device.utilities.network.base_network_utility import NetworkUtility


class BalenaNetworkUtility(NetworkUtility):
    def __init__(self):
        super().__init__()
        self.wifi_connect_commad = "/usr/src/app/wifi-connect"
        self.logger.info("BalenaNetworkUtility: __init__")
        self.NET_CONFIGURED = settings.DATA_PATH + "/network.configured"
        self.AP_NAME = "PFC-" + os.getenv("RESIN_DEVICE_NAME_AT_INIT")

    # Override is_connected() to check to see if we need to start up wifi-connect (first boot)

    def is_connected(self) -> bool:
        base_connected = super().is_connected()
        # check for network_configured flag.
        if not base_connected and not Path(self.NET_CONFIGURED).exists():
            self._start_wifi_connect(True)  # Clear out old config anyway
            Path(self.NET_CONFIGURED).touch()
        return base_connected

    def get_wifi_ssids(self, exclude_hidden: bool = True, exclude_beaglebones: bool = True) -> List[Dict[str, str]]:
        self.logger.info("BalenaNetworkUtility: get_wifi_ssids: passing")
        return []

    def join_wifi(self, ssid: str, password: str) -> None:
        self.logger.info("BalenaNetworkUtility: join_wifi: calling _start_wifi_connect()")
        return self._start_wifi_connect()

    def join_wifi_advance(self, ssid_name: str, passphrase: str, hidden_ssid: str, security: str, eap: str,
                          identity: str, phase2: str) -> None:
        self.logger.info("BalenaNetworkUtility: join_wifi_advanced: calling _start_wifi_connect()")
        return self._start_wifi_connect()

    def delete_wifis(self) -> None:
        self.logger.info("BalenaNetworkUtility: delete_wifis: calling _start_wifi_connect(True)")
        return self._start_wifi_connect(True)

    def _start_wifi_connect(self, disconnect: bool = False) -> None:
        self.logger.info("BalenaNetworkUtility in _start_wifi_connect()")
        if disconnect:
            self.logger.debug("Disconnecting from current wifi")
        # Path(self.NET_CONFIGURED).unlink()
        subprocess.call(["scripts/platform/reset_balena_app.sh"])
        # subprocess.call([self.wifi_connect_commad, "-s", self.AP_NAME, "-o", "8765", "-u", "/usr/src/app/ui"])
        return