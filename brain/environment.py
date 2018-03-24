# Import python modules
import logging, time


class Environment(object):
    """ A shared memory object is used to report sensor data, 
    set desired setpoints, and command actuators. """

    # Initialize logger
    logger = logging.getLogger(__name__)

    # Initialize sensor parameters
    sampling_rate_seconds = 2
    sampling_duration_seconds = None


    def __init__(self):
        """ Initializes environment object. """
        self.actuator = {"desired": {}, "reported": {}}
        self.sensor = {"desired": {}, "reported": {}}
        self.reported_sensor_stats = {
            "individual": {
                "instantaneous": {},
                "average": {}
            },
            "group": {
                "instantaneous": {},
                "average": {}
            }
        }
        

    def report_sensor_value(self, sensor, variable, value):
        """ Report sensor value to sensor dict and reported sensor 
            stats dict. """

        # Update individual instantaneous
        by_type = self.reported_sensor_stats["individual"]["instantaneous"]
        if variable not in by_type:
            by_type[variable] = {}
        by_var = self.reported_sensor_stats["individual"]["instantaneous"][variable]
        by_var[sensor] = value

        # Update individual average
        by_type = self.reported_sensor_stats["individual"]["average"]
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
        by_var_i = self.reported_sensor_stats["individual"]["instantaneous"][variable]
        num_sensors = 0
        total = 0
        for sensor in by_var_i:
            total += by_var_i[sensor]
            num_sensors += 1
        new_value = total / num_sensors
        self.reported_sensor_stats["group"]["instantaneous"][variable] = {"value": new_value, "samples": num_sensors}

        # Update group average
        by_type = self.reported_sensor_stats["group"]["average"]
        if variable not in by_type:
            by_type[variable] = {"value": value, "samples": 1}
        else:
            stored_value = by_type[variable]["value"]
            stored_samples = by_type[variable]["samples"]
            new_samples = (stored_samples + 1)
            new_value = (stored_value * stored_samples + value) / new_samples
            by_type[variable]["value"] = new_value
            by_type[variable]["samples"] = new_samples

        # Update simple sensor value
        self.sensor["reported"][variable] = self.reported_sensor_stats["group"]["instantaneous"][variable]["value"]


    def reset_average(self):
        """ Reset the data in the reported sensor averages. Should be reset 
            each time environment state is stored in database. """
        self.reported_sensor_stats["individual"]["average"] = {}
        self.reported_sensor_stats["group"]["average"] = {}
        self.logger.debug("Reset average")