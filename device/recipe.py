# Import python modules
import logging, time, json, threading, os

# Import all possible states & errors
from device.utility.states import States
from device.utility.errors import Errors

# Import db models from django
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()
from app.models import ParsedRecipe


class Recipe:
    """ Recipe handler. Manages recipe state machine and interactions
    	with recipe table in database. """

    # Initialize logger
    logger = logging.getLogger(__name__)

    # Initialize state and error lists
    states = States()
    errors = Errors()

    # Initialize state & error variables
    _state = None
    _error = None

    # Initialize recipe file
    recipe = None


    def load_recipe_file(self, file):
        """ Loads recipe file into database. Parses phased recipe into
            by-the-minute entries containing environment state dicts in 
            the database. """
        self.recipe = json.load(open(file))

        # Clear parsed recipe table in database
        ParsedRecipe.objects.all().delete()

        # Parse recipe file into database
        minute_counter = 0
        for phase in self.recipe["phases"]:
            phase_name = phase["name"]
            for i in range(phase["repeat"]):
                for cycle in phase["cycles"]:
                    # Get environment name and state + cycle name
                    environment_name = cycle["environment"]
                    environment_state = self.recipe["environments"][environment_name]
                    cycle_name = cycle["name"]

                    # Get duration
                    if "duration_hours" in cycle:
                        duration_hours = cycle["duration_hours"]
                        duration_minutes = duration_hours * 1 # TODO: set this to 60
                    elif "duration_minutes" in cycle:
                        duration_minutes = cycle["duration_minutes"]
                    else:
                        self.logger.error("Invalid cycle duration. Must be duration_minutes or duration_hours")
                        return
                    
                    # Write to database
                    for minute in range(duration_minutes):
                        minute_counter += 1
                        ParsedRecipe.objects.create(
                            minute = minute_counter,
                            phase = phase_name,
                            cycle = cycle_name,
                            environment_name = environment_name,
                            environment_state = environment_state
                        )







            




    # def timestamp_minutes(self):
    #     """ Get timestamp in minutes. """
    #     return int(time.time() / 60

    # self.timestamp_minutes()
# 

# 