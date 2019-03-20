import subprocess
from typing import List, Dict

from device.utilities.network.network import NetworkUtility

class BalenaNetworkUtility(NetworkUtility):
    def __init__(self):
        super().__init__()
        self.wifi_connect_commad = "wifi-connect"
        self.logger.info("BalenaNetworkUtility: __init__")

    def get_wifi_ssids(self, exclude_hidden: bool = True, exclude_beaglebones: bool = True) -> List[Dict[str, str]]:
        self.logger.info("BalenaNetworkUtility: get_wifi_ssids: passing")
        pass
        #return super().get_wifi_ssids(exclude_hidden, exclude_beaglebones)

    def join_wifi(self, ssid: str, password: str) -> None:
        self.logger.info("BalenaNetworkUtility: join_wifi: calling _start_wifi_connect()")
        return self._start_wifi_connect()

    def join_wifi_advance(self, ssid_name: str, passphrase: str, hidden_ssid: str, security: str, eap: str,
                          identity: str, phase2: str) -> None:
        self.logger.info("BalenaNetworkUtility: join_wifi_advanced: calling _start_wifi_connect()")
        return self._start_wifi_connect()
        #super().join_wifi_advance(ssid_name, passphrase, hidden_ssid, security, eap, identity, phase2)

    def delete_wifis(self) -> None:
        self.logger.info("BalenaNetworkUtility: delete_wifis: calling _start_wifi_connect(True)")
        return self._start_wifi_connect(True)

    def _start_wifi_connect(self, disconnect: bool = False) -> None:
        self.logger.info("BalenaNetworkUtility in _start_wifi_connect()")
        clear_flag = "--clear=false"
        if disconnect:
            self.logger.debug("Disconnecting from current wifi")
            clear_flag = "--clear=true"
        subprocess.call([self.wifi_connect_commad, clear_flag])
        return