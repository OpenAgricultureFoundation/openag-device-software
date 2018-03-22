""" Description of what file does. """

# Import python modules
import logging, time, threading

# Define environment class
class Environment(object):
    """ Description """

    # Initialize logger
    logger = logging.getLogger(__name__)

    # Initialize sensor parameters
    sampling_rate_seconds = 2
    sampling_duration_seconds = None


    def __init__(self):
        """ Description. """

        # Extract all variables from config
        variables = ["air_temperature", "air_humidity"]

        # Initialize raw environment dictionary
        self._raw = {}
        for variable in variables:
            self._raw[variable] = {}

        # Initialize instantantaneous environment dictionary
        self._inst = {}
        for variable in variables:
            self._inst[variable] = None

        # Initialize average environment dictionary
        self._avg = {}
        for variable in variables:
            self._avg[variable] = {}


    def set(self, peripheral, variable, value):
        """ Description. """

        # Update raw environment dictionary
        self._raw[variable][peripheral] = value
        self.logger.debug('Set raw {} ({}): {}'.format(variable, peripheral, value))

        # Update instantaneous environment dictionary 
        # Average values from all peripheral devices with identical variables
        inst_value = 0
        num_peripherals = 0
        for peripheral in self._raw[variable]:
            inst_value += self._raw[variable][peripheral]
            num_peripherals += 1
        inst_value /= num_peripherals
        self._inst[variable] = inst_value
        self.logger.debug("Set instantaneous {}: {}".format(variable, inst_value))

        # Update average environment dictionary
        # Average value for each peripheral
        if peripheral not in self._avg[variable]:
            avg_value = value
            samples = 1
        else:
            stored_avg = self._avg[variable][peripheral]["value"]
            stored_samples = self._avg[variable][peripheral]["samples"]
            samples = stored_samples + 1
            avg_value = (stored_avg*stored_samples + value) / samples
        self._avg[variable][peripheral] = {"value": avg_value, "samples": samples}
        self.logger.debug("Set average {} ({}): {}, samples: {}".format(variable, peripheral, avg_value, samples))


    def get(self, variable):
        """ Description. """
        if variable in self.inst:
            return self._inst[variable]
        else:
            return None


    def reset_average(self):
        self._avg = {}
        for variable in variables:
            self._avg[variable] = {}
        self.logger.debug("Reset average")
