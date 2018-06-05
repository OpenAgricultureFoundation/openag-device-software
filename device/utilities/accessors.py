# Import standard python modules
import threading
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