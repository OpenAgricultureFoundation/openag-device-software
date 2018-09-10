# Import python modules
import threading, subprocess, pyudev, numpy

# Import python types
from typing import Dict, Optional, List, Any


def listify_dict(dict_: Dict[str, float]) -> List[float]:
    """Converts a dict into a list."""
    list_ = []
    for key, value in dict_.items():
        list_.append(value)
    return list_


def vectorize_dict(dict_: Dict[str, float]) -> numpy.ndarray:
    """Converts a dict into a vector."""
    list_ = listify_dict(dict_)
    vector = numpy.array(list_)
    return vector


def matrixify_nested_dict(nested_dict: Dict[str, Dict[str, float]]) -> numpy.ndarray:
    """Converts a nested dict into a matrix."""
    nested_list = []
    for key, dict_ in nested_dict.items():
        nested_list.append(listify_dict(dict_))
    raw_matrix = numpy.array(nested_list)
    matrix = numpy.transpose(raw_matrix)
    return matrix


def dictify_list(list_: List[Any], reference_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a list into a dictionary."""
    dict_ = {}
    for index, key in enumerate(reference_dict):
        dict_[key] = list_[index]
    return dict_


def set_nested_dict_safely(
    nested_dict: Dict, keys: List, value: str, lock: threading.Lock
) -> None:
    """ Safely sets value in nested dict. """
    with lock:
        for key in keys[:-1]:
            if key not in nested_dict:
                nested_dict[key] = {}
            nested_dict = nested_dict[key]
        nested_dict[keys[-1]] = value


def get_nested_dict_safely(
    nested_dict: Dict, keys: List, return_type: Optional[Any] = None
) -> Any:
    """ Safely gets value from nested dict. """
    for key in keys:
        if key not in nested_dict:
            return None
        nested_dict = nested_dict[key]

    # On last key, nested dict becomes value
    value = nested_dict

    # Check if return type specified
    if return_type != None:
        return return_type(value)

    # Otherwise return un-type cast value
    return value


def get_peripheral_config(peripheral_configs: List, name: str) -> Dict:
    """ Gets peripheral config from list of peripheral configs. """
    for peripheral_config in peripheral_configs:
        if peripheral_config["name"] == name:
            return peripheral_config
    raise KeyError("`{}` not in peripheral configs".format(name))


def usb_device_matches(
    device_path: str, vendor_id: int, product_id: int, friendly: bool = True
) -> bool:
    """ Checks if a usb device at specified path matches provided vendor
        and product ids. """

    # TODO: Add error handling
    # TODO: Handle multiple operating systems

    # Convert device path to real path if friendly
    if friendly:
        command = "udevadm info --name={} -q path".format(device_path)
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        device_path = str(output.strip(), encoding="utf-8")

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
