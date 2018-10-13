# Import standard python modules
import subprocess, socket, urllib.request

# Import python types
from typing import List, Dict, Union

# Import device utilities
from device.utilities import system
from device.utilities.logger import Logger

# Initialize file paths
GET_WIFIS_SCRIPT_PATH = "scripts/get_wifis.sh"
CONNECT_WIFI_SCRIPT_PATH = "scripts/connect_wifi.sh"
DELETE_WIFI_SCRIPT_PATH = "scripts/delete_all_wifi_connections.sh"

# Initialize logger
logger = Logger("NetoworkUtility", "connect")


def internet_is_connected() -> bool:
    """Checks if device is connected to the internet."""
    try:
        urllib.request.urlopen("http://google.com")
        return True
    except urllib.error.URLError:  # type: ignore
        return False


def get_ip_address() -> str:
    """Gets ip address of the active network interface."""
    logger.debug("Getting ip address")

    # Get ip address
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception as e:
        message = "Unable to get ip address, unhandled exception: {}".format(type(e))
        logger.exception(message)
        return "Unknown"


def get_wifi_access_points(
    exclude_hidden: bool = True, exclude_beaglebones: bool = True
) -> List[Dict[str, str]]:
    """Gets wifi access points. Currently only works for wifi beaglebones."""
    logger.debug("Getting wifi access points")

    # Check system is a beaglebone wifi
    if not system.is_wifi_bbb():
        logger.error("Unable to get wifi access points, system not a wifi beaglebone")
        return []

    # Build command
    command = [GET_WIFIS_SCRIPT_PATH]

    # Run command
    try:
        with subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as process1:
            output = process1.stdout.read().decode("utf-8")
            output += process1.stderr.read().decode("utf-8")
            print(output)
    except Exception as e:
        logger.exception("Unable get wifis, unhandled exception: `{}`".format(type(e)))
        return []

    return []

    # Parse command output to get list of wifi access points
    wifi_access_points = []
    lines = output.splitlines()
    for line in lines:

        # Get active id
        tokens = re.findall("\*\S*", line)
        if len(tokens) == 1:
            active_id = tokens[0]
            connected = True
        else:
            active_id = ""
            connected = False

        # Get pre-shared key (psk)
        tokens = re.findall("wifi_\S*", line)
        if len(tokens) == 1:
            psk = tokens[0]
        else:
            psk = ""

        # Get service set identifier (ssid)
        ssid = line.replace(active_id, "").replace(psk, "").strip()
        if ssid == "":
            ssid = "<Hidden SSID>"
            hidden = True
        else:
            hidden = False

        # Check if excluding hidden access points
        if exclude_hidden and hidden:
            continue

        # Check if excluding beaglebone acccess points
        if exclude_beaglebones and ssid.startswith("Beaglebone"):
            continue

        # Add access point to list
        wifi_access_points.append(
            {"ssid": ssid, "psk": psk, "connected": connected, "hidden": hidden}
        )

    # Successfully got wifi access points
    return wifi_access_points


def join_wifi(wifi: str, password: str) -> bool:
    """Joins specified wifi access point. Currently only works for wifi beaglebones. 
    Returns true on success, false on failure"""
    logger.debug("Joining wifi")

    # Check system is a beaglebone wifi
    if not system.is_wifi_bbb():
        logger.error("Unable to join wifi, system not a wifi beaglebone")
        return False

    # Not sure why we are doing this?
    if len(password) == 0:
        password = ""

    # Build command
    command = [CONNECT_WIFI_SCRIPT_PATH, wifi, password]

    # Execute command
    try:
        with subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as process1:
            output = process1.stdout.read().decode("utf-8")
            output += process1.stderr.read().decode("utf-8")
            return True
            # time.sleep(5)  # Time for networking stack to init # This shouldn't be here
    except Exception as e:
        logger.exception("Unable to join wifi, unhandled exception: {}".format(type(e)))
        return False


def delete_wifi_connections() -> bool:
    """Deletes all wifi connections. Currently only works for wifi beaglebones.
    Returns true on success, false on failure. TODO: Should probably just catch then
    re-raise exception."""
    logger.debug("Deleting wifi connections")

    # Check system is a beaglebone wifi
    if not system.is_wifi_bbb():
        logger.error("Unable to delete wifi connections, system not a wifi beaglebone")
        return False

    # Disconnect from active wifi access points
    try:
        wifi_access_points = get_wifi_access_points(
            exclude_hidden=False, exclude_beaglebones=False
        )
        for wifi_access_point in wifi_access_points:
            if wifi_access_point["connected"]:
                psk = wifi_access_point["psk"]
                command = ["connmanctl", "disconnect", psk]
                subprocess.run(command)
    except Exception as e:
        message = "Unable to delete wifi connections, unable to disconnect from active "
        message += "wifi access points, unhandled exception: {}".format(type(e))
        logger.exception(message)
        return False

    # Remove all wifi configs
    try:
        command = [DELETE_WIFIS_SCRIPT_PATH]
        with subprocess.run(command):
            return True
    except Exception as e:
        message = "Unable to delete wifi connections, "
        message += "unhandled exception: {}".format(type(e))
        logger.exception(message)
        return False
