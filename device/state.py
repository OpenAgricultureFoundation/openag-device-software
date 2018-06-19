# Import standard python modules
import threading

# Import device utilities
from device.utilities.accessors import set_nested_dict_safely
from device.utilities.accessors import get_nested_dict_safely


class State(object):
    """ Shared memory object used to store and transmit 
        state between threads. """
    device = {}
    environment = {}
    recipe = {}
    peripherals = {}
    controllers = {}  
    iot = {}  


    def set_environment_reported_sensor_value(self, sensor, variable, value, simple=False):
        """ Sets reported sensor value to shared environment state. """

        # TODO: Clean this up

        # Ensure valid dict structure
        if "reported_sensor_stats" not in self.environment:
            self.environment["reported_sensor_stats"] = {}

        # Individual
        if "individual" not in self.environment["reported_sensor_stats"]:
            self.environment["reported_sensor_stats"]["individual"] = {}
        if "instantaneous" not in self.environment["reported_sensor_stats"]["individual"]:
            self.environment["reported_sensor_stats"]["individual"]["instantaneous"] = {}
        if "average" not in self.environment["reported_sensor_stats"]["individual"]:
            self.environment["reported_sensor_stats"]["individual"]["average"] = {}

        # Group
        if "group" not in self.environment["reported_sensor_stats"]:
            self.environment["reported_sensor_stats"]["group"] = {}
        if "instantaneous" not in self.environment["reported_sensor_stats"]["group"]:
            self.environment["reported_sensor_stats"]["group"]["instantaneous"] = {}
        if "average" not in self.environment["reported_sensor_stats"]["group"]:
            self.environment["reported_sensor_stats"]["group"]["average"] = {}

        # Sensor
        if "sensor" not in self.environment:
            self.environment["sensor"] = {}
        if "reported" not in self.environment["sensor"]:
            self.environment["sensor"]["reported"] = {}

        # Force simple if value is None (don't want to try averaging `None`)
        if value == None:
            simple = True

        with threading.Lock():
            # Update individual instantaneous
            by_type = self.environment["reported_sensor_stats"]["individual"]["instantaneous"]
            if variable not in by_type:
                by_type[variable] = {}
            by_var = self.environment["reported_sensor_stats"]["individual"]["instantaneous"][variable]
            by_var[sensor] = value

            if simple:
                # Update simple sensor value with reported value
                self.environment["sensor"]["reported"][variable] = value

            else:
                # Update individual average
                by_type = self.environment["reported_sensor_stats"]["individual"]["average"]
                if variable not in by_type:
                    by_type[variable] = {}
                if sensor not in by_type:
                    by_type[sensor] = {"value": value, "samples": 1}
                else:
                    stored_value = by_type[sensor]["value"]
                    stored_samples = by_type[sensor]["samples"]
                    new_samples = (stored_samples + 1)
                    new_value = (stored_value * stored_samples + value) / new_samples
                    by_type[sensor]["value"] = new_value
                    by_type[sensor]["samples"] = new_samples

                # Update group instantaneous
                by_var_i = self.environment["reported_sensor_stats"]["individual"]["instantaneous"][variable]
                num_sensors = 0
                total = 0
                for sensor in by_var_i:
                    if by_var_i[sensor] != None:
                        total += by_var_i[sensor]
                        num_sensors += 1
                new_value = total / num_sensors
                self.environment["reported_sensor_stats"]["group"]["instantaneous"][variable] = {"value": new_value, "samples": num_sensors}

                # Update group average
                by_type = self.environment["reported_sensor_stats"]["group"]["average"]
                if variable not in by_type:
                    by_type[variable] = {"value": value, "samples": 1}
                else:
                    stored_value = by_type[variable]["value"]
                    stored_samples = by_type[variable]["samples"]
                    new_samples = (stored_samples + 1)
                    new_value = (stored_value * stored_samples + value) / new_samples
                    by_type[variable]["value"] = new_value
                    by_type[variable]["samples"] = new_samples

                # Update simple sensor value with instantaneous group value
                self.environment["sensor"]["reported"][variable] = self.environment["reported_sensor_stats"]["group"]["instantaneous"][variable]["value"]


    def set_environment_desired_sensor_value(self, variable, value):
        """ Sets desired sensor value to shared environment state. """
        set_nested_dict_safely(self.environment, ["sensor", "desired", variable], value)          


    def set_environment_reported_actuator_value(self, variable, value):
        """ Sets reported actuator value to shared environment state. """
        set_nested_dict_safely(self.environment, ["actuator", "reported", variable], value)          


    def set_environment_desired_actuator_value(self, variable, value):
        """ Sets desired actuator value to shared environment state. """
        set_nested_dict_safely(self.environment, ["actuator", "desired", variable], value)          


    def get_environment_reported_sensor_value(self, variable):
        """ Gets reported sensor value from shared environment state. """
        return get_nested_dict_safely(self.environment, ["sensor", "reported", variable]) 


    def get_environment_desired_sensor_value(self, variable):
        """ Gets desired sensor value from shared environment state. """
        return get_nested_dict_safely(self.environment, ["sensor", "desired", variable]) 


    def get_environment_reported_actuator_value(self, variable):
        """ Gets reported actuator value from shared environment state. """
        return get_nested_dict_safely(self.environment, ["actuator", "reported", variable]) 


    def get_environment_desired_actuator_value(self, variable):
        """ Gets desired actuator value from shared environment state. """
        return get_nested_dict_safely(self.environment, ["actuator", "desired", variable]) 


    def set_peripheral_value(self, peripheral, variable, value):
        """ Sets peripheral to shared peripheral state. """
        set_nested_dict_safely(self.peripherals, [peripheral, variable], value)         


    def get_peripheral_value(self, peripheral, variable):
        """ Gets peripheral value from shared peripheral state. """
        return get_nested_dict_safely(self.peripherals, [peripheral, variable])


    def set_peripheral_reported_sensor_value(self, peripheral, variable, value):
        """ Sets reported sensor value to shared peripheral state. """
        set_nested_dict_safely(self.peripherals, [peripheral, "sensor", "reported", variable], value)          


    def set_peripheral_desired_sensor_value(self, peripheral, variable, value):
        """ Sets desired sensor value to shared peripheral state. """
        set_nested_dict_safely(self.peripherals, [peripheral, "sensor", "desired", variable], value)          


    def set_peripheral_reported_actuator_value(self, peripheral, variable, value):
        """ Sets reported actuator value to shared peripheral state. """
        set_nested_dict_safely(self.peripherals, [peripheral, "actuator", "reported", variable], value)          


    def set_peripheral_desired_actuator_value(self, peripheral, variable, value):
        """ Sets desired actuator value to shared peripheral state. """
        set_nested_dict_safely(self.peripherals, [peripheral, "actuator", "desired", variable], value)          


    def get_peripheral_reported_sensor_value(self, peripheral, variable):
        """ Gets reported sensor value from shared peripheral state. """
        return get_nested_dict_safely(self.peripherals, [peripheral, "sensor", "reported", variable])


    def get_peripheral_desired_sensor_value(self, peripheral, variable):
        """ Gets desired sensor value from shared peripheral state. """
        return get_nested_dict_safely(self.peripherals, [peripheral, "sensor", "desired", variable]) 


    def get_peripheral_reported_actuator_value(self, peripheral, variable):
        """ Gets reported actuator value from shared peripheral state. """
        return get_nested_dict_safely(self.peripherals, [peripheral, "actuator", "reported", variable]) 


    def get_peripheral_desired_actuator_value(self, peripheral, variable):
        """ Gets desired actuator value from shared peripheral state. """
        return get_nested_dict_safely(self.peripherals, [peripheral, "actuator", "desired", variable]) 

