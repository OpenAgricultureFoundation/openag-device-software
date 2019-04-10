import subprocess
from pathlib import Path
from typing import List, Dict
from django.conf import settings
import os
import NetworkManager

from device.utilities.network.base_network_utility import NetworkUtility


class BalenaNetworkUtility(NetworkUtility):
    def __init__(self) -> None:
        super().__init__()
        self.wifi_connect_commad = "/usr/src/app/wifi-connect"
        self.logger.debug("BalenaNetworkUtility: __init__")
        self.NET_CONFIGURED = settings.DATA_PATH + "/network.configured"
        self.AP_NAME = "PFC-" + str(os.getenv("RESIN_DEVICE_NAME_AT_INIT"))

    # Override is_connected() to check to see if we need to start up wifi-connect (first boot)

    def is_connected(self) -> bool:
        base_connected = super().is_connected()
        # check for network_configured flag.
        if not base_connected and not Path(self.NET_CONFIGURED).exists():
            self._start_wifi_connect(True)  # Clear out old config anyway
            ## Never reached: Path(self.NET_CONFIGURED).touch()
        return base_connected

    def get_wifi_ssids(
        self, exclude_hidden: bool = True, exclude_beaglebones: bool = True
    ) -> List[Dict[str, str]]:
        self.logger.debug("BalenaNetworkUtility: get_wifi_ssids: passing")
        return []

    def join_wifi(self, ssid: str, password: str) -> None:
        self.logger.debug(
            "BalenaNetworkUtility: join_wifi: calling _start_wifi_connect()"
        )
        return self._start_wifi_connect()

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
        self.logger.debug(
            "BalenaNetworkUtility: join_wifi_advanced: calling _start_wifi_connect()"
        )
        return self._start_wifi_connect()

    def delete_wifis(self) -> None:
        self.logger.debug(
            "BalenaNetworkUtility: delete_wifis: calling _start_wifi_connect(True)"
        )
        return self._start_wifi_connect(True)

    def _start_wifi_connect(self, disconnect: bool = False) -> None:
        """Disconnect all wifi known connections, then start up wifi-connect to create captive portal AP for setup"""
        self.logger.debug("BalenaNetworkUtility in _start_wifi_connect()")

        # Remove the /data/network.configured file that is used to bypass wificonnect in run_django.sh
        Path(self.NET_CONFIGURED).unlink()

        # Get all known connections
        connections = NetworkManager.Settings.ListConnections()

        # Delete the '802-11-wireless' connections
        for connection in connections:
            if connection.GetSettings()["connection"]["type"] == "802-11-wireless":
                self.logger.debug(
                    "BalenaNetworkUtility: Deleting connection "
                    + connection.GetSettings()["connection"]["id"]
                )
                connection.Delete()

        # Script to call the balena supervisor internal API to reboot the device
        subprocess.call(["scripts/platform/reset_balena_app.sh"])
        return
