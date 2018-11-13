# Import standard python modules
import pyudev, glob, subprocess

# Import python types
from typing import List

# Import device utilities
from device.utilities.logger import Logger

# Initialize logger
logger = Logger("USBUtility", "device")


def device_matches(
    device_path: str, vendor_id: int, product_id: int, friendly: bool = True
) -> bool:
    """Checks if a usb device at specified path matches vendor id and product id."""
    logger.debug("Checking if device matches")

    # Convert device path to real path if friendly
    # TODO: Explain friendly path...
    if friendly:
        command = "udevadm info --name={} -q path".format(device_path)
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        device_path = str(output.strip(), encoding="utf-8")

    # Get device info
    context = pyudev.Context()
    device = pyudev.Device.from_path(context, device_path)
    device_vendor_id = int("0x" + device.get("ID_VENDOR_ID"), 16)
    device_product_id = int("0x" + device.get("ID_MODEL_ID"), 16)

    # Check if ids match
    if vendor_id != device_vendor_id or product_id != device_product_id:
        logger.debug("Device does not match")
        return False

    # USB device matches
    logger.debug("Device matches")
    return True


def get_camera_paths(vendor_id: int, product_id: int) -> List[str]:
    """Returns list of cameras that match the provided vendor id and product id."""
    logger.debug("Getting camera paths")

    # List all camera paths
    camera_paths = glob.glob("/dev/video*")

    # Get valid camera paths
    valid_camera_paths = []
    for camera_path in camera_paths:
        if device_matches(camera_path, vendor_id, product_id):
            valid_camera_paths.append(camera_path)

    # Successfully got camera paths
    logger.debug("Got camera paths: {}".format(valid_camera_paths))
    return valid_camera_paths
