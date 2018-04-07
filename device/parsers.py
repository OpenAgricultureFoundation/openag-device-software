# Import standard python modules
import logging


class RecipeParser:
    """ Parses recipes. """

    def parse(self, recipe_dict):
        """ Parses recipe into state transitions. """
        transitions = []
        minute_counter = 0
        for phase in recipe_dict["phases"]:
            phase_name = phase["name"]
            for i in range(phase["repeat"]):
                for cycle in phase["cycles"]:
                    # Get environment object and cycle name
                    environment_key = cycle["environment"]
                    environment = recipe_dict["environments"][environment_key]
                    cycle_name = cycle["name"]

                    # Get duration
                    if "duration_hours" in cycle:
                        duration_hours = cycle["duration_hours"]
                        duration_minutes = duration_hours * 60
                    elif "duration_minutes" in cycle:
                        duration_minutes = cycle["duration_minutes"]
                    else:
                        raise KeyError("Could not find 'duration_minutes' or 'duration_hours' in cycle")

                    # Make shallow copy of env so we can pop a property locally
                    environment_copy = dict(environment) 
                    environment_name = environment_copy["name"]
                    del environment_copy["name"]
                    environment_state = environment_copy

                    # Write recipe transition to database
                    transitions.append({
                        "minute": minute_counter,
                        "phase": phase_name,
                        "cycle": cycle_name,
                        "environment_name": environment_name,
                        "environment_state": environment_state})

                    # Increment minute counter
                    minute_counter += duration_minutes

        # Set recipe end
        transitions.append({
            "minute": minute_counter,
            "phase": "End",
            "cycle": "End",
            "environment_name": "End",
            "environment_state": {}})

        # Return state transitions
        return transitions