# Import standard python modules
import subprocess, os, re

# Import device utilities
from device.utilities.logger import Logger

# Initialize file paths
DEVICE_CONFIG_PATH = "data/config/device.txt"

# Initialize logger
logger = Logger("SystemUtility", "system")
logger.debug("Initializing utility")

# Initialize filepaths
BBB_SERIAL_SCRIPT_PATH = "scripts/get_bbb_serial.sh"
WIFI_ACCESS_POINT_SCRIPT_PATH = "scripts/get_access_point.sh"


def is_raspberry_pi_3() -> bool:
    """Check if current system is a raspberry pi 3"""

    try:
        # Read cpu info
        with open("/proc/cpuinfo", "r") as infile:
            cpu_info = infile.read()

        # Check for the processor used in raspi 3
        if "BCM2835" in cpu_info:
            return True
        else:
            return False
    except:
        # TODO: Handle this exception
        return False


def is_beaglebone() -> bool:
    """Checks if current system is a beaglebone. TODO: Don't use bash functions."""
    logger.debug("Checking if system is a beaglebone")

    # Build command
    command = ["cat", "/etc/dogtag"]

    # Execute command
    try:
        with subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as process:
            output = process.stdout.read().decode("utf-8")
            output += process.stderr.read().decode("utf-8")
    except Exception as e:
        message = "Unable to check if system is a beaglebone, unhandled exception: {}".format(
            type(e)
        )
        logger.exception(message)

    # Check if system is not a beaglebone
    if "Beagle" not in output:
        logger.debug("System is not a beaglebone")
        return False

    # System is a beaglebone
    logger.debug("System is a beaglebone")
    return True


def is_wifi_beaglebone() -> bool:
    """Checks if system is a wifi beaglebone."""
    logger.debug("Checking if system is a wifi beaglebone")

    # Check if system is a beaglebone
    if not is_beaglebone():
        logger.debug("System is not a wifi beaglebone")
        return False

    # Build command
    command = ["ifconfig", "wlan0"]

    # Execute command
    try:
        with subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as process:
            output = process.stdout.read().decode("utf-8")
            output += process.stderr.read().decode("utf-8")

    except Exception as e:
        message = "Unable to check if system is a wifi beaglebone, "
        message += "unhandled exception: {}".format(type(e))
        logger.exception(message)

    # Check if system does not has wifi
    if "wlan0: flags" not in output:
        logger.debug("System is not a wifi beaglebone")
        return False

    # System is a wifi beaglebone
    logger.debug("System is a wifi beaglbone")
    return True


def beaglebone_serial_number() -> str:
    """Gets the beaglebone serial number."""
    logger.debug("Getting beaglebone serial number")

    # Check system is a beaglebone
    if not is_beaglebone():
        logger.debug("Unable to get serial number, system not a beaglebone")
        return "Unknown"

    # Build command
    command = [BBB_SERIAL_SCRIPT_PATH]

    # Execute command
    try:
        with subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as process:
            output = process.stdout.read().decode("utf-8")
            output += process.stderr.read().decode("utf-8")
    except Exception as e:
        message = "Unable to get beaglebone serial number, unhandled exception: {}".format(
            type(e)
        )
        logger.exception(message)
        return "Unknown"

    # Parse output
    serial_number = str(output.strip())

    # Successfully got serial number
    logger.debug("Successfully got serial number: {}".format(serial_number))
    return serial_number


def raspberry_pi_3_serial_number() -> str:
    """Gets the serial number from a raspberry pi 3."""

    # Check system is a raspberry pi 3
    if not is_raspberry_pi_3():
        logger.debug(
            "Unable to get raspberry pi 3 serial number, system not a raspberry pi 3"
        )
        return "Unknown"

    try:
        # Read cpu info
        with open("/proc/cpuinfo", "r") as infile:
            cpu_info = infile.read()

        # Parse out serial number
        output = re.search(r"Serial.*", cpu_info).group()  # type: ignore
        serial_number = str(output.replace("Serial", "").replace(":", "").strip())

    except Exception as e:
        message = "Unable to get raspberry pi 3 serial number, unhandled exception: {}".format(
            type(e)
        )
        logger.exception(message)
        return "Unknown"

    # Successfully got serial number
    logger.debug("Successfully got serial number: {}".format(serial_number))
    return serial_number


def remote_device_ui_url() -> str:
    """Gets remote device ui url. Currently only works for beaglebones."""
    logger.debug("Getting remote device ui url")

    # TODO: Make this more flexible...e.g. if system not a beaglebone, generate a
    # unique ui url...be able to handle ngrok if enabled...

    # Check if device is a beaglebone
    if is_beaglebone():
        serial_number = beaglebone_serial_number()
        url = "https://{}.serveo.net".format(serial_number)
        return url
    elif is_raspberry_pi_3():
        serial_number = raspberry_pi_3_serial_number()
        url = "https://{}.serveo.net".format(serial_number)
        return url

    # Device is not a beaglebone
    return "Remote device UI currently only supported for beaglebone or raspberry pi 3"


def device_config_name() -> str:
    """Gets device config name from file."""
    logger.debug("Getting device config name")

    # Get device config name
    if os.path.exists(DEVICE_CONFIG_PATH):
        with open(DEVICE_CONFIG_PATH) as f:
            device_config_name = f.readline().strip()
    else:
        device_config_name = "unspecified"

    # Successfully got device config name
    logger.debug("Device config name: {}".format(device_config_name))
    return device_config_name


def beaglebone_wifi_access_point_name() -> str:
    """Gets the beaglebone wifi access point name."""
    logger.debug("Getting beaglebone wifi access point name")

    # Check system is a beaglebone
    if not is_beaglebone():
        logger.debug("Unable to get beaglebone AP, system not a beaglebone")
        return "Unknown"

    # Build command
    command = [WIFI_ACCESS_POINT_SCRIPT_PATH]

    # Execute command
    try:
        with subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as process:
            output = process.stdout.read().decode("utf-8")
            output += process.stderr.read().decode("utf-8")
    except Exception as e:
        message = "Unable to get beaglebone serial number, unhandled exception: {}".format(
            type(e)
        )
        logger.exception(message)
        return "Unknown"

    # Parse output
    wifi_access_point_name = str(output.strip())

    # Successfully got serial number
    debug_message = "Successfully got wifi access point name: {}".format(
        wifi_access_point_name
    )
    logger.debug(debug_message)
    return wifi_access_point_name
