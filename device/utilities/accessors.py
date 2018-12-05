# Import python modules
import threading, subprocess, numpy

# Import python types
from typing import Dict, Optional, List, Any

# Import device utilities
from device.utilities import constants


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
    nested_dict: Dict, keys: List, value: Any, lock: threading.RLock
) -> None:
    """ Safely sets value in nested dict. """
    with lock:
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

    # On last key, nested dict becomes value
    value = nested_dict

    # Otherwise return un-type cast value
    return value


def floatify_string(value: str) -> float:
    """Converts a num string (e.g. 10M or 10K) to a float."""
    unit = value[-1]
    number = float(value[:-1])
    if unit.lower() == "k":
        return number * float(constants.KILOBYTE)
    elif unit.lower() == "m":
        return number * float(constants.MEGABYTE)
    elif unit.lower() == "g":
        return number * float(constants.GIGABYTE)
    else:
        raise ValueError("Invalid unit type `{}`".format(unit))


# TODO: Make these general case
def get_peripheral_config(
    peripheral_configs: List[Dict[str, Any]], name: str
) -> Dict[str, Any]:
    """ Gets peripheral config from list of peripheral configs. """
    for peripheral_config in peripheral_configs:
        if peripheral_config["name"] == name:
            return peripheral_config
    raise KeyError("`{}` not in peripheral configs".format(name))


def get_controller_config(
    controller_configs: List[Dict[str, Any]], name: str
) -> Dict[str, Any]:
    """ Gets controller config from list of peripheral configs. """
    for controller_config in controller_configs:
        if controller_config["name"] == name:
            return controller_config
    raise KeyError("`{}` not in controller configs".format(name))
