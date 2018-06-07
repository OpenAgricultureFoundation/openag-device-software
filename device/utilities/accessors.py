# Import python modules
import threading, subprocess, pyudev
from typing import Dict, Optional, List, Any

def set_nested_dict_safely(nested_dict: Dict, keys: List, value: str) -> None:  
    """ Safely sets value in nested dict. """
    with threading.Lock():
        for key in keys[:-1]:
            if key not in nested_dict:
                nested_dict[key] = {}
            nested_dict = nested_dict[key]
        nested_dict[keys[-1]] = value


def get_nested_dict_safely(nested_dict: Dict, keys: List) -> Any:
    """ Safely gets value from nested dict. """
    for key in keys:
        if key not in nested_dict:
            return None
        nested_dict = nested_dict[key]
    return nested_dict # on last key, nested dict becomes value


def get_peripheral_config(peripheral_configs: List, name: str) -> Dict:
    """ Gets peripheral config from list of peripheral configs. """
    for peripheral_config in peripheral_configs:
        if peripheral_config["name"] == name:
            return peripheral_config
    raise KeyError("`{}` not in peripheral configs".format(name))



def usb_device_matches(device_path: str, vendor_id: int, product_id: int, friendly: bool = True) -> bool:
    """ Checks if a usb device at specified path matches provided vendor
        and product ids. """

    # TODO: Add error handling
    # TODO: Handle multiple operating systems

    # Convert device path to real path if friendly
    if friendly:
        command = "udevadm info --name={} -q path".format(device_path)
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        device_path = str(output.strip(), encoding='utf-8')

    # Get device info
    context = pyudev.Context()
    device = pyudev.Device.from_path(context, device_path)
    vid = int("0x" + device.get("ID_VENDOR_ID"), 16)
    pid = int("0x" + device.get("ID_MODEL_ID"), 16)

    # Check if ids match
    if vendor_id != vid or product_id != pid:
        return False

    # USB device matches!
    return True