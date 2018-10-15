# Import standard python modules
import subprocess

# Import device utilities
from device.utilities.logger import Logger

# Initialize file paths
DEVICE_CONFIG_PATH = "data/config/device.txt"

# Initialize logger
logger = Logger("SystemUtility", "system")
logger.debug("Initializing utility")


def is_beaglebone() -> bool:
    """Checks if current system is a beaglebone."""
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
        logger.debug("Unable to get beaglebone serial number, system not a beaglebone")
        return "Unknown"

    # Build command
    command = ["scripts/get_bbb_sn.sh"]

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


def remote_device_ui_url() -> str:
    """Gets remote device ui url. Currently only works for beaglebones."""
    logger.debug("Getting remote device ui url")

    # TODO: Make this more flexible...e.g. if system not a beaglebone, generate a
    # unique ui url...be able to handle ngrok if enabled...

    # Check if device is a beaglebone
    if is_beaglebone():
        serial_number = beaglebone_serial_number()
        url = "{}.serveo.net".format(serial_number)
        return url

    # Device is not a beaglebone
    return "Remote device UI currently only supported for beaglebones"


def get_device_id_from_file() -> str:  # Should probably be in iot?
    return "JIBBIES"


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
