# Import python modules
import logging, time

# Import variable info
from device.utility.variables import Variables


class Environment(object):
    """ A shared memory object is used to report sensor data, 
    set desired setpoints, and command actuators. """

    # Initialize logger
    logger = logging.getLogger(__name__)

    # Initialize variable info
    variables = Variables()

    # Initialize environment objects
    actuator = {"desired": {}, "reported": {}}
    sensor = {"desired": {}, "reported": {}}
    reported_sensor_stats = {
        "individual": {
            "instantaneous": {},
            "average": {}
        },
        "group": {
            "instantaneous": {},
            "average": {}
        }
    }


    # def environment_state(self):
    #     """ Get environment state from environment object. """
    #     environment_state = {}
    #     environment_state["actuator"] = self.actuator
    #     environment_state["sensor"] = self.sensor
    #     environment_state["reported_sensor_stats"] = self.reported_sensor_stats
    #     return environment_state


    # def set_desired_sensor_values(self, environment_dict):
    #     """ Sets desired sensor values from provided environment dict. """
    #     for variable in environment_dict:
    #         self.sensor["desired"][variable] = environment_dict[variable]
        

    # def report_sensor_value(self, sensor, variable, value, simple=False):
    #     """ Report sensor value to sensor dict and reported sensor 
    #         stats dict. """

    #     # Update individual instantaneous
    #     by_type = self.reported_sensor_stats["individual"]["instantaneous"]
    #     if variable not in by_type:
    #         by_type[variable] = {}
    #     by_var = self.reported_sensor_stats["individual"]["instantaneous"][variable]
    #     by_var[sensor] = value

    #     if simple:
    #         # Update simple sensor value with reported value
    #         self.sensor["reported"][variable] = value

    #     else:
    #         # Update individual average
    #         by_type = self.reported_sensor_stats["individual"]["average"]
    #         if variable not in by_type:
    #             by_type[variable] = {}
    #         if sensor not in by_type:
    #             by_type[sensor] = {"value": value, "samples": 1}
    #         else:
    #             stored_value = by_type[sensor]["value"]
    #             stored_samples = by_type[sensor]["samples"]
    #             new_samples = (stored_samples + 1)
    #             new_value = (stored_value * stored_samples + value) / new_samples
    #             by_type[sensor]["value"] = new_value
    #             by_type[sensor]["samples"] = new_samples

    #         # Update group instantaneous
    #         by_var_i = self.reported_sensor_stats["individual"]["instantaneous"][variable]
    #         num_sensors = 0
    #         total = 0
    #         for sensor in by_var_i:
    #             if by_var_i[sensor] != None:
    #                 total += by_var_i[sensor]
    #                 num_sensors += 1
    #         new_value = total / num_sensors
    #         self.reported_sensor_stats["group"]["instantaneous"][variable] = {"value": new_value, "samples": num_sensors}

    #         # Update group average
    #         by_type = self.reported_sensor_stats["group"]["average"]
    #         if variable not in by_type:
    #             by_type[variable] = {"value": value, "samples": 1}
    #         else:
    #             stored_value = by_type[variable]["value"]
    #             stored_samples = by_type[variable]["samples"]
    #             new_samples = (stored_samples + 1)
    #             new_value = (stored_value * stored_samples + value) / new_samples
    #             by_type[variable]["value"] = new_value
    #             by_type[variable]["samples"] = new_samples

    #         # Update simple sensor value with instantaneous group value
    #         self.sensor["reported"][variable] = self.reported_sensor_stats["group"]["instantaneous"][variable]["value"]


    # def report_actuator_value(self, actuator, variable, value):
    #     """ Report an actuator value. """
    #     self.actuator["reported"][variable] = value


    def reset_average(self):
        """ Reset the data in the reported sensor averages. Should be reset 
            each time environment state is stored in database. """
        self.reported_sensor_stats["individual"]["average"] = {}
        self.reported_sensor_stats["group"]["average"] = {}
        self.logger.debug("Reset average")


    def get_log(self, sensors=True, actuators=True):
        """ Returns log string of current sensor and actuator values. """
        log = ""
        if sensors:
            log += "\n    Sensors:" + self.get_peripheral_log(self.sensor)
        if actuators:
            log += "\n    Actuators:" + self.get_peripheral_log(self.actuator)
        return log



    def get_peripheral_log(self, peripheral):
        """ Gets log of current reported --> desired value for peripheral. """
        log = ""

        # Log all variables in reported
        for variable in peripheral["reported"]:
            name = self.variables.info[variable]["name"]
            unit = self.variables.info[variable]["unit"]
            reported = str(peripheral["reported"][variable])
            if variable in peripheral["desired"]:
                desired = str(peripheral["desired"][variable])
            else:
                desired = "None"
            log += self.get_log_line(name, unit, reported, desired)

        # Log remaining variables in desired
        for variable in peripheral["desired"]:
            if variable not in peripheral["reported"]:
                name = self.variables.info[variable]["name"]
                unit = self.variables.info[variable]["unit"]
                desired = str(peripheral["desired"][variable])
                reported = "None"
                log += self.get_log_line(name, unit, reported, desired)

        # Check for empty log
        if log == "":
            log = "\n        None"

        return log


    def get_log_line(self, name, unit, reported, desired):
        """ Returns a log line string for a reported --> desired value. """
        line = "\n        " + name + " (" + unit + "): " + reported + " --> " + desired
        return line


