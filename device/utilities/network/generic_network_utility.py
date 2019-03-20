import os, subprocess
from typing import List, Dict

from device.utilities.network.network import NetworkUtility


class GenericNetworkUtility(NetworkUtility):

    def __init__(self):
        super(GenericNetworkUtility, self).__init__()
        self.GET_WIFI_SSIDS_SCRIPT_PATH = "scripts/network/get_wifi_ssids.sh"
        self.JOIN_WIFI_SCRIPT_PATH = "scripts/network/join_wifi.sh"
        self.JOIN_WIFI_ADVANCED_SCRIPT_PATH = "scripts/network/join_wifi_advanced.sh"

    def get_wifi_ssids(self, exclude_hidden: bool = True, exclude_beaglebones: bool = True) -> List[Dict[str, str]]:
        self.logger.debug("Getting wifi ssids")

        if os.getenv("IS_WIFI_ENABLED", "false") != "true":
            self.logger.error("Unable to get wifi ssids, system not wifi enabled")
            return []

        command = [self.GET_WIFI_SSIDS_SCRIPT_PATH]

        try:
            with subprocess.Popen(
                    command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ) as process1:
                output = process1.stdout.read().decode("utf-8")
                output += process1.stderr.read().decode("utf-8")
        except Exception as e:
            self.logger.exception("Unable to get wifi ssids, unhandled exception: `{}`".format(e))
            return []

        wifi_ssids = output.splitlines()

        for index, wifi_ssid in enumerate(wifi_ssids):
            # Remove beaglebone access points
            if exclude_beaglebones and wifi_ssid.startswith("Beaglebone"):
                del wifi_ssid[index]

            # Remove junk hex values that sometimes get reported from raspberry pi
            if "\\x00" in wifi_ssid:
                del wifi_ssids[index]

        return wifi_ssids

    def join_wifi(self, ssid: str, password: str) -> None:
        """Joins specified wifi ssid if platform is wifi enabled."""
        self.logger.debug("Joining wifi: {}".format(ssid))

        # Check system is a wifi enabled
        if os.getenv("IS_WIFI_ENABLED") != "true":
            message = "Unable to join wifi, system not wifi enabled"
            self.logger.error(message)
            raise SystemError(message)

        # Not sure why we are doing this?
        if len(password) == 0:
            password = ""

        # Build command
        command = [self.JOIN_WIFI_SCRIPT_PATH, ssid, password]

        # Execute command
        try:
            with subprocess.Popen(
                    command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ) as process1:
                output = process1.stdout.read().decode("utf-8")
                output += process1.stderr.read().decode("utf-8")
            self.logger.debug(output)
        except Exception as e:
            self.logger.exception("Unable to join wifi, unhandled exception: {}".format(type(e)))
            raise

    def join_wifi_advance(self, ssid_name: str, passphrase: str, hidden_ssid: str, security: str, eap: str,
                          identity: str, phase2: str) -> None:
        """Joins specified wifi ssid if platform is wifi enabled."""
        self.logger.debug("Joining wifi: {}".format(ssid_name))

        # Check system is a wifi enabled
        if os.getenv("IS_WIFI_ENABLED") != "true":
            message = "Unable to join wifi, system not wifi enabled"
            self.logger.error(message)
            raise SystemError(message)

        # Not sure why we are doing this?
        if len(passphrase) == 0:
            password = ""

        # Build command
        command = [self.JOIN_WIFI_ADVANCED_SCRIPT_PATH,
                   ssid_name,
                   passphrase,
                   hidden_ssid,
                   security,
                   eap,
                   identity,
                   phase2
                   ]

        # Execute command
        try:
            with subprocess.Popen(
                    command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ) as process1:
                output = process1.stdout.read().decode("utf-8")
                output += process1.stderr.read().decode("utf-8")
            self.logger.debug(output)
        except Exception as e:
            self.logger.exception("Unable to join wifi, unhandled exception: {}".format(type(e)))
            raise