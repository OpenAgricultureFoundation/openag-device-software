# Import standard python modules
import subprocess

# Import device utilities
from device.utilities.logger import Logger


# Initialize logger
logger = Logger("SystemUtility", "connect")  # TODO: fix this log file


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


def get_beaglebone_serial_number() -> str:
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
