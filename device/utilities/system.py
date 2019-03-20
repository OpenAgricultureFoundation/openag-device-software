# Import standard python modules
import subprocess, os, re

# Import device utilities
from device.utilities.logger import Logger

from django.conf import settings

# Initialize file paths
# DEVICE_CONFIG_PATH = "data/config/device.txt"
# DATA_PATH = os.getenv("STORAGE_LOCATION", "data")
DEVICE_CONFIG_PATH = settings.DATA_PATH + "/config/device.txt"

# Initialize logger
logger = Logger("SystemUtility", "system")
logger.debug("Initializing utility")


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
