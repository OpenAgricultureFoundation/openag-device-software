# Import standard python modules
import json, time

# Import app models
from app.models import StateModel
from app.models import EventModel
from app.models import SensorVariableModel
from app.models import ActuatorVariableModel


def get_device_state_value(key):
    """ Gets device state value from state table in database """

    # Get device state dict
    if not StateModel.objects.filter(pk=1).exists():
        return None
    else:
        state = StateModel.objects.get(pk=1)
        device_state_dict = json.loads(state.device)

    # Get value for key
    if key in device_state_dict:
        return device_state_dict[key]
    else:
        return None


def get_recipe_state_value(key):
    """ Gets recipe state value from state table in database """

    # Get recipe state dict
    if not StateModel.objects.filter(pk=1).exists():
        return None
    else:
        state = StateModel.objects.get(pk=1)
        recipe_state_dict = json.loads(state.recipe)
    
    # Get value for key
    if key in recipe_state_dict:
        return recipe_state_dict[key]
    else:
        return None


def get_environment_dict():
    """ Gets environment dict from state table in database. """
    if not StateModel.objects.filter(pk=1).exists():
        return None
    else:
        state = StateModel.objects.get(pk=1)
        return json.loads(state.environment)


def get_peripheral_dict():
    """ Gets peripheral dict from state table in database. """
    if not StateModel.objects.filter(pk=1).exists():
        return None
    else:
        state = StateModel.objects.get(pk=1)
        return json.loads(state.peripherals)


def get_sensor_variable_info(variable_key):
    """ Gets sensor variable info from sensor variable table in database. """
    if not SensorVariableModel.objects.filter(key=variable_key).exists():
        return None
    else:
        variable = SensorVariableModel.objects.get(key=variable_key)
        variable_dict = json.loads(variable.json)
        return variable_dict["info"]


def get_actuator_variable_info(variable_key):
    """ Gets actuator variable info from actuator variable table in database. """
    if not ActuatorVariableModel.objects.filter(key=variable_key).exists():
        return None
    else:
        variable = ActuatorVariableModel.objects.get(key=variable_key)
        variable_dict = json.loads(variable.json)
        return variable_dict["info"]


def manage_event(event_request, timeout_seconds=3, update_interval_seconds=0.1):
    """ Manages an event request. Creates new event in database, waits for 
        event response, returns event response or timeout error. """

    # Create event in database
    event = EventModel.objects.create(request=event_request)

    # Wait for response
    start_time_seconds = time.time()
    while time.time() - start_time_seconds < timeout_seconds:
        event_response = EventModel.objects.get(pk=event.id).response
        if event_response != None:
            status = event_response["status"]
            response = {"message": event_response["message"]}
            return response, status
        # Check for response every 100ms
        time.sleep(update_interval_seconds)

    # Return timeout error
    status=500
    response = {"message": "Event response timed out"}
    return response, status