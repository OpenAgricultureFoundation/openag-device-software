# Import standard python modules
import json, threading, logging, time, json
import uuid as uuid_module

# Import app models
from app.models import State

# Import app utilities
from device.utility.mode import Mode
from device.utility.format import Format

# Import app models
from app.models import Recipe as RecipeModel


class Recipe():
    # Initialize logger
    extra = {"console_name":"Recipe Viewer", "file_name": "recipe_viewer"}
    logger = logging.getLogger(__name__)
    logger = logging.LoggerAdapter(logger, extra)

    try:
        # TODO: Stop being lazy and do this the right way...
        state = State.objects.filter(pk=1).first()
        dict_ = json.loads(state.recipe)
        json = dict_["recipe"]
        name = json["name"]
        started = dict_["start_datestring"]
        progress = dict_["percent_complete_string"]
        time_elapsed = dict_["time_elapsed_string"]
        time_remaining = dict_["time_remaining_string"]
        current_phase = dict_["current_phase"]
        current_cycle = dict_["current_cycle"]
        current_environment = dict_["current_environment_name"]
    except:
        self.logger.exception("Unable to initialize recipe viewer")
        self.logger.critical("Unable to initialize recipe viewer")


    @property
    def mode(self):
        """ Gets mode from shared state. """
        if "mode" in self.state.recipe:
            return self.state.recipe["mode"]
        else:
            return None


    @property
    def commanded_mode(self):
        """ Gets commanded mode from shared state. """
        if "commanded_mode" in self.state.recipe:
            return self.state.recipe["commanded_mode"]
        else:
            return None


    @commanded_mode.setter
    def commanded_mode(self, value):
        """ Safely updates commanded mode in shared state. """
        with threading.Lock():
            self.state.recipe["commanded_mode"] = value


    def create(self, request):
        """ Creates a recipe provided a json file. """
        self.logger.info("Received request to create recipe")

        # Validate json
        response, status = self.validate(request)
        if status != 200:
            self.logger.info("Recipe is invalid")
            self.logger.info("{}".format(response))
            return response, status

        # Create entry in database
        self.logger.info("Creating recipe in database")
        RecipeModel.objects.create(recipe_json=request["recipe_json"])

        # Return success response
        response = {"message": "Created recipe!"}
        status = 201
        return response, status


    def validate(self, request):
        """ Validates recipe json. """
        self.logger.info("Validating recipe")

        # Get recipe json and create recipe dict
        if "recipe_json" not in request:
            status = 400
            response = {"message": "Request does not contain `recipe_json` key"}
            return response, status 
        else:
            recipe_dict = json.loads(request["recipe_json"])

        # Verify uuid uniqueness if supplied
        if "uuid" in recipe_dict and self.uuid_exists(recipe_dict["uuid"]):
            status = 400
            response = {"message": "Recipe uuid already exists"}
            return response, status

        """ TODO: Verify values and/or value types (e.g. date is formatted 
            properly, name is a string and not a list) """

        # Verify format key
        if "format" not in recipe_dict or recipe_dict["format"] == None:
            status = 400
            response = {"message": "Recipe json does not contain `format`"}
            return response, status
        
        # Get format type
        if "type" not in recipe_dict["format"] or recipe_dict["format"]["type"] == None:
            status = 400
            response = {"message": "Recipe json does not contain `type`"}
            return response, status
        else:
            format_type = recipe_dict["format"]["type"]

        # Get format version 
        if "version" not in recipe_dict["format"] or recipe_dict["format"]["version"] == None:
            status = 400
            response = {"message": "Recipe json does not contain `version`"}
            return response, status
        else:
            format_version = recipe_dict["format"]["version"]

        # Verify format specific parameters
        if format_type == "phased-environment" and format_version == Format.VERSION_1:
            # Verify phased-environment v1 keys 
            if "name" not in recipe_dict or recipe_dict["name"] == None:
                status = 400
                response = {"message": "Recipe json does not contain `name`"}
                return response, status
            if "date_created" not in recipe_dict or recipe_dict["date_created"] == None:
                status = 400
                response = {"message": "Recipe json does not contain `date_created`"}
                return response, status
            if "author" not in recipe_dict or recipe_dict["author"] == None:
                status = 400
                response = {"message": "Request json does not contain `author`"}
                return response, status
            if "seeds" not in recipe_dict or recipe_dict["seeds"] == None:
                status = 400
                response = {"message": "Request json does not contain `seeds`"}
                return response, status

            # Verify able to generate phased-environment v1.0 phase transitions
            phase_transitions, error_message = self.generate_transitions_phased_environment_v1(recipe_dict)
            if phase_transitions == None:
                status = 400
                response = {"message": error_message}
                return response, status
        else: 
            # Unsupported format / version
            status = 400
            response = {"message": "Recipe format / version not supported"}
            return response, status

        # Return valid recipe format
        status = 200
        response = {"message": "Recipe is valid!"}
        return response, status


    def uuid_exists(self, uuid):
        """ Checks if uuid is unique. """
        self.logger.info("Checking if uuid is unique")
        return RecipeModel.objects.filter(uuid=uuid).exists()


    def generate_transitions_phased_environment_v1(self, recipe_dict):
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

        


    def stop(self, request):
        """ Stops a recipe. Returns true once recipe is stopped. 
            Logs exception if recipe mode does not change modes 
            within 3 seconds. """

        self.logger.info("Received request to stop recipe")

        # # Check a recipe is running
        # if self.mode == Mode.RUN:
        #     data = {"message": "No recipe currently running!"}
        #     return Response(data, status=200)

        # # Stop the recipe
        # if self.stop_recipe(timeout=1):   
        #     data = {"message": "Recipe stopped!"}
        #     return Response(data, status=200)
        # else:
        #     data = {"message": "Unable to stop recipe. Request timed out."}
        #     return Response(data, status=500)

        # Send command to change mode
        # self.commanded_mode = Mode.STOP

        # # Make sure recipe thread changes mode
        # start_time = time.time()
        # while time.time() - start_time < 3:
        #     if self.mode == Mode.STOP:
        #         return True
        
        # Log error event 
        # TODO: raise an exception
        # self.logger.critical("Recipe did not change modes within 3 seconds.")

        response = {"message": "Recipe stopped!"}
        status = 200
        return response, status


