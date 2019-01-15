# Import standard python modules
import os, sys, subprocess, socket, urllib.request, re

# Import python types
from typing import List, Dict, Union

# REMOVE ME!!
ROOT_DIR = os.environ["PROJECT_ROOT"]
sys.path.append(ROOT_DIR)
os.chdir(ROOT_DIR)

# Import device utilities
from device.utilities import system
from device.utilities.logger import Logger

# Initialize file paths
GET_WIFI_SSIDS_SCRIPT_PATH = "scripts/get_wifi_ssids.sh"
JOIN_WIFI_SCRIPT_PATH = "scripts/join_wifi.sh"
DELETE_WIFIS_SCRIPT_PATH = "scripts/delete_all_wifi_connections.sh"
ENABLE_RASPI_ACCESS_POINT_SCRIPT_PATH = "scripts/enable_raspi_access_point.sh"
DISABLE_RASPI_ACCESS_POINT_SCRIPT_PATH = "scripts/disable_raspi_access_point.sh"
REMOVE_RASPI_PREV_WIFI_ENTRY_SCRIPT_PATH = "scripts/remove_raspi_prev_wifi_entry.sh"


# Initialize logger
logger = Logger("NetworkUtility", "network")


def is_connected() -> bool:
    """Checks if connected to network."""
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
        return str(s.getsockname()[0])
    except Exception as e:
        message = "Unable to get ip address, unhandled exception: {}".format(type(e))
        logger.exception(message)
        return "Unknown"


def get_wifi_ssids(
    exclude_hidden: bool = True, exclude_beaglebones: bool = True
) -> List[Dict[str, str]]:
    """Gets wifi ssids for wifi enabled devices."""
    logger.debug("Getting wifi ssids")

    # Check system is wifi enabled
    if os.getenv("IS_WIFI_ENABLED", "false") != "true":
        logger.error("Unable to get wifi ssids, system not wifi enabled")
        return []

    # Build command
    command = [GET_WIFI_SSIDS_SCRIPT_PATH]

    # Run command
    try:
        with subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as process1:
            output = process1.stdout.read().decode("utf-8")
            output += process1.stderr.read().decode("utf-8")
    except Exception as e:
        logger.exception("Unable get wifis, unhandled exception: `{}`".format(type(e)))
        return []

    # Parse command output to get list of wifi access points
    wifi_ssids = output.splitlines()

    # Clean up ssid list
    for index, wifi_ssid in enumerate(wifi_ssids):

        # Remove beaglebone access points
        if exclude_beaglebones and wifi_ssid.startswith("Beaglebone"):
            del wifi_ssid[index]

        # Remove junk hex values that sometimes get reported from raspberry pi
        if "\\x00" in wifi_ssid:
            del wifi_ssids[index]

    # Successfully got wifi access points
    return wifi_ssids


def join_wifi(ssid: str, password: str) -> None:
    """Joins specified wifi ssid if platform is wifi enabled."""
    logger.debug("Joining wifi: {}".format(ssid))

    # Check system is a wifi enabled
    if os.getenv("IS_WIFI_ENABLED") != "true":
        message = "Unable to join wifi, system not wifi enabled"
        logger.error(message)
        raise SystemError(message)

    # Not sure why we are doing this?
    if len(password) == 0:
        password = ""

    # Build command
    command = [JOIN_WIFI_SCRIPT_PATH, ssid, password]

    # Execute command
    try:
        with subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as process1:
            output = process1.stdout.read().decode("utf-8")
            output += process1.stderr.read().decode("utf-8")
        logger.debug(output)
    except Exception as e:
        logger.exception("Unable to join wifi, unhandled exception: {}".format(type(e)))
        raise


def join_wifi_advanced(
    ssid_name: str,
    passphrase: str,
    hidden_ssid: str,
    security: str,
    eap: str,
    identity: str,
    phase2: str,
) -> None:
    """Joins specified wifi access point with advanced config args."""
    logger.debug("Joining wifi advanced")

    # Ensure passphrase is a string?
    if len(passphrase) == 0:
        passphrase = ""

    # Build command
    command = [
        "scripts/advanced_connect_wifi.sh",
        ssid_name,
        passphrase,
        hidden_ssid,
        security,
        eap,
        identity,
        phase2,
    ]

    # Execute command
    try:
        subprocess.run(command)
    except Exception as e:
        message = "Unable to join wifi advanced, unhandled exception".format(type(e))
        logger.exception(message)
        raise


def delete_wifis() -> None:
    """Deletes all wifi connections. Currently only works for wifi beaglebones.
    Returns true on success, false on failure. TODO: Should probably just catch then
    re-raise exception."""
    logger.debug("Deleting wifis")

    # Check system is a wifi beaglebone
    if os.getenv("PLATFORM") != "beaglebone-wireless":
        message = "Unable to delete wifis, system not a wifi beaglebone"
        logger.error(message)
        raise SystemError(message)

    # Disconnect from active wifi access points
    # TODO: How important is this? Will this break beaglebones...
    # try:
    #     wifi_access_points = get_wifi_access_points(
    #         exclude_hidden=False, exclude_beaglebones=False
    #     )
    #     for wifi_access_point in wifi_access_points:
    #         if wifi_access_point["connected"]:
    #             psk = wifi_access_point["psk"]
    #             command = ["connmanctl", "disconnect", psk]
    #             subprocess.run(command)
    # except Exception as e:
    #     message = "Unable to delete wifis, unable to disconnect from active "
    #     message += "wifi access points, unhandled exception: {}".format(type(e))
    #     logger.exception(message)
    #     raise

    # Remove all wifi configs
    try:
        command = [DELETE_WIFIS_SCRIPT_PATH]
        subprocess.run(command)
    except Exception as e:
        message = "Unable to delete wifis, "
        message += "unhandled exception: {}".format(type(e))
        logger.exception(message)
        raise


def enable_raspi_access_point() -> None:
    """Enables the raspberry pi access point."""
    logger.debug("Enabling raspberry pi access point")

    # Check system is a raspberry pi
    if "raspberry-pi" not in str(os.getenv("PLATFORM")):
        message = "Unable to enable raspberry pi access point, platform not a raspberry pi"
        logger.error(message)
        raise SystemError(message)

    # Build command
    command = [ENABLE_RASPI_ACCESS_POINT_SCRIPT_PATH]

    # Execute command
    try:
        with subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as process1:
            output = process1.stdout.read().decode("utf-8")
            output += process1.stderr.read().decode("utf-8")
    except Exception as e:
        logger.exception(
            "Unable to enable raspberry pi access point, unhandled exception: {}".format(
                type(e)
            )
        )
        raise


def disable_raspi_access_point() -> None:
    """Disables the raspberry pi access point."""
    logger.debug("Disabling raspberry pi access point.")

    # Check system is a raspberry pi
    if "raspberry-pi" not in str(os.getenv("PLATFORM")):
        message = "Unable to disable raspberry pi access point, platform not a raspberry pi"
        logger.error(message)
        raise SystemError(message)

    # Build command
    command = [DISABLE_RASPI_ACCESS_POINT_SCRIPT_PATH]

    # Execute command
    try:
        with subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as process1:
            output = process1.stdout.read().decode("utf-8")
            output += process1.stderr.read().decode("utf-8")
    except Exception as e:
        logger.exception(
            "Unable to disable raspberry pi access point, unhandled exception: {}".format(
                type(e)
            )
        )
        raise


def remove_raspi_prev_wifi_entry() -> None:
    """Removes previous wifi entry."""
    logger.debug("Removing previous wifi entry")

    # Check system is a raspberry pi
    if "raspberry-pi" not in str(os.getenv("PLATFORM")):
        message = "Unable to remove previous wifi entry, platform not a raspberry pi"
        logger.error(message)
        raise SystemError(message)

    # Build command
    command = [REMOVE_RASPI_PREV_WIFI_ENTRY_SCRIPT_PATH]

    # Execute command
    try:
        with subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as process1:
            output = process1.stdout.read().decode("utf-8")
            output += process1.stderr.read().decode("utf-8")
    except Exception as e:
        logger.exception(
            "Unable to remove previous wifi entry, unhandled exception: {}".format(
                type(e)
            )
        )
        raise


# def get_wifi_access_points(
#     exclude_hidden: bool = True, exclude_beaglebones: bool = True
# ) -> List[Dict[str, str]]:
#     """Gets wifi access points for wifi enabled devices."""
#     logger.debug("Getting wifi access points")

#     # Check system is wifi enabled
#     if os.getenv("IS_WIFI_ENABLED", "false") != "true":
#         logger.error("Unable to get wifi access points, system not wifi enabled")
#         return []

#     # Build command
#     command = [GET_WIFI_SSIDS_SCRIPT_PATH]

#     # Run command
#     try:
#         with subprocess.Popen(
#             command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
#         ) as process1:
#             output = process1.stdout.read().decode("utf-8")
#             output += process1.stderr.read().decode("utf-8")
#     except Exception as e:
#         logger.exception("Unable get wifis, unhandled exception: `{}`".format(type(e)))
#         return []

#     # Parse command output to get list of wifi access points
#     wifi_access_points = []
#     lines = output.splitlines()

#     for line in lines:

#         # Get active id
#         tokens = re.findall("\*\S*", line)
#         if len(tokens) == 1:
#             active_id = tokens[0]
#             connected = True
#         else:
#             active_id = ""
#             connected = False

#         # Get pre-shared key (psk)
#         tokens = re.findall("wifi_\S*", line)
#         if len(tokens) == 1:
#             psk = tokens[0]
#         else:
#             psk = ""

#         # Get service set identifier (ssid)
#         ssid = line.replace(active_id, "").replace(psk, "").strip()
#         if ssid == "":
#             ssid = "<Hidden SSID>"
#             hidden = True
#         else:
#             hidden = False

#         # Check if excluding hidden access points
#         if exclude_hidden and hidden:
#             continue

#         # Check if excluding beaglebone acccess points
#         if exclude_beaglebones and ssid.startswith("Beaglebone"):
#             continue

#         # Add access point to list
#         wifi_access_points.append(
#             {"ssid": ssid, "psk": psk, "connected": connected, "hidden": hidden}
#         )

#     # Successfully got wifi access points
#     return wifi_access_points
