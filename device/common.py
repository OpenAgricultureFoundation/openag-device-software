# Import standard python modules
import logging

# Import device utilities
from device.utility.format import Format


class Common:
    """ Common functions used between device components. """
    
    # Initialize logger
    extra = {"console_name":"Common", "file_name": "common"}
    logger = logging.getLogger(__name__)
    logger = logging.LoggerAdapter(logger, extra)


    def generate_recipe_transitions(self, recipe_dict):
        """ Generate phase transitions for recipes of multiple formats. """
        self.logger.debug("Generating recipe transitions")

        # TODO: handle multiple recipe cases once we have multiple formats

        # Generate transitions for phased-environment v1
        return self.generate_recipe_transitions_phased_environment_v1(recipe_dict)


    def generate_recipe_transitions_phased_environment_v1(self, recipe_dict):
        """ Tries to generate phase transitions for phased-environment v1,
            returns phase transitions and error message. """
        try: 
            phase_transitions = []
            minute_counter = 0
            for phase in recipe_dict["phases"]:
                phase_name = phase["name"]
                for i in range(phase["repeat"]):
                    for cycle in phase["cycles"]:
                        # Get environment name and state + cycle name
                        environment_name = cycle["environment"]
                        environment_state = recipe_dict["environments"][environment_name]
                        cycle_name = cycle["name"]

                        # Get duration
                        if "duration_hours" in cycle:
                            duration_hours = cycle["duration_hours"]
                            duration_minutes = duration_hours * 60
                        elif "duration_minutes" in cycle:
                            duration_minutes = cycle["duration_minutes"]
                        else:
                            raise KeyError("Could not find 'duration_minutes' or 'duration_hours' in cycle")

                        # Write recipe transition to database
                        phase_transitions.append({
                            "minute": minute_counter,
                            "phase": phase_name,
                            "cycle": cycle_name,
                            "environment_name": environment_name,
                            "environment_state": environment_state})

                        # Increment minute counter
                        minute_counter += duration_minutes

            # Set recipe end
            phase_transitions.append({
                "minute": minute_counter,
                "phase": "End",
                "cycle": "End",
                "environment_name": "End",
                "environment_state": {}})

            # Successfully generate phase transitions
            error_message = None
            return phase_transitions, error_message
        
        except:
            # TODO: Handle multiple exception types
            phase_transitions = None
            error_message = "Unable to generate transitions. "
            return phase_transitions, error_message