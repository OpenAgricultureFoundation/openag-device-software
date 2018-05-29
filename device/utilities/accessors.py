# Import standard python modules
import threading


def set_nested_dict_safely(nested_dict, keys, value):  
    """ Safely sets value in nested dict. """
    with threading.Lock():
        for key in keys[:-1]:
            if key not in nested_dict:
                nested_dict[key] = {}
            nested_dict = nested_dict[key]
        nested_dict[keys[-1]] = value


def get_nested_dict_safely(nested_dict, keys):
    """ Safely gets value from nested dict. """
    for key in keys:
        if key not in nested_dict:
            return None
        nested_dict = nested_dict[key]
    return nested_dict # on last key, nested dict becomes value