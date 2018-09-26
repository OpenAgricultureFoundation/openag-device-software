# Import standard python modules
import json, time, logging

# Import app models
from app.models import StateModel
from app.models import EventModel
from app.models import SensorVariableModel
from app.models import ActuatorVariableModel


class Common(object):
    extra = {"console_name": "Common", "file_name": "common"}
    logger = logging.getLogger(__name__)
    logger = logging.LoggerAdapter(logger, extra)

    def get_sensor_variable_info(self, variable_key):
        """ Gets sensor variable info from sensor variable table in database. """
        if not SensorVariableModel.objects.filter(key=variable_key).exists():
            self.logger.info(
                "Unable to get sensor variable info, `{}` does not exist".format(
                    variable_key
                )
            )
            return None
        else:
            variable = SensorVariableModel.objects.get(key=variable_key)
            variable_dict = json.loads(variable.json)
            return variable_dict["info"]

    def get_actuator_variable_info(self, variable_key):
        """ Gets actuator variable info from actuator variable table in database. """
        if not ActuatorVariableModel.objects.filter(key=variable_key).exists():
            self.logger.info(
                "Unable to get actuator variable info, `{}` does not exist".format(
                    variable_key
                )
            )
            return None
        else:
            variable = ActuatorVariableModel.objects.get(key=variable_key)
            variable_dict = json.loads(variable.json)
            return variable_dict["info"]

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

    def get_iot_dict():
        """ Gets iot dict from state table in database. """
        if not StateModel.objects.filter(pk=1).exists():
            return None
        else:
            state = StateModel.objects.get(pk=1)
            return json.loads(state.iot)

    def get_resource_dict():
        """ Gets resource dict from state table in database. """
        if not StateModel.objects.filter(pk=1).exists():
            return None
        else:
            state = StateModel.objects.get(pk=1)
            return json.loads(state.resource)

    def get_connect_dict():
        """ Gets connect dict from state table in database. """
        if not StateModel.objects.filter(pk=1).exists():
            return None
        else:
            state = StateModel.objects.get(pk=1)
            return json.loads(state.connect)

    def get_upgrade_dict():
        """ Gets upgrade dict from state table in database. """
        if not StateModel.objects.filter(pk=1).exists():
            return None
        else:
            state = StateModel.objects.get(pk=1)
            return json.loads(state.upgrade)

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
        status = 500
        response = {"message": "Event response timed out"}
        return response, status
