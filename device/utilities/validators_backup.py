# Import standard python modules
import json, logging

# Import device parsers
from device.parsers import RecipeParser

# Import app models
from app.models import RecipeModel



class Validator:
    """ Parent class for validators. """
    extra = {"console_name":"Validator", "file_name": "validator"}
    logger = logging.getLogger(__name__)
    logger = logging.LoggerAdapter(logger, extra)





class PeripheralSetupValidator:
    """ Validates peripheral setup dict. """

    # Initialize logger
    extra = {"console_name":"Validator", "file_name": "validator"}
    logger = logging.getLogger(__name__)
    logger = logging.LoggerAdapter(logger, extra)


    def validate(self, setup_json, filepath=False):
        """ Validates peripheral config. Returns message on error, 
            none on success. """
        self.logger.debug("Validating {}".format(setup_json))

        # Validate json
        try:
            if filepath:
                setup_dict = json.load(open(setup_json))
            else:
                setup_dict = json.loads(setup_json)
        except json.decoder.JSONDecodeError:
            return "Invalid JSON"
        
        # Validate keys
        error_message = self.validate_keys(setup_dict)
        if error_message != None:
            return error_message

        # TODO: Validate variables


    def validate_keys(self, setup_dict):
        """ Validates keys in peripheral setup dict. """
       
        try:
            # Verify top level keys
            parent_key = ""
            setup_dict["name"]
            setup_dict["uuid"]
            setup_dict["module_name"]
            setup_dict["class_name"]
            setup_dict["parameters"]
            setup_dict["info"]
            
            # Verify nested parameters keys
            parent_key = "parameters "
            setup_dict["parameters"]["variables"]
            setup_dict["parameters"]["communication"]

            # Verify nested parameters variables keys
            parent_key = "parameters variables "
            setup_dict["parameters"]["variables"]["sensors"]
            setup_dict["parameters"]["variables"]["actuators"]

            # Verify nested info keys
            parent_key = "info "
            setup_dict["info"]["variables"]

            # Verify nested description keys
            parent_key = "info variables "
            setup_dict["info"]["variables"]["sensors"]
            setup_dict["info"]["variables"]["actuators"]

        except KeyError as e:
            error_message = "Peripheral setup " + parent_key + "`{}` key is required".format(e.args[0])
            return error_message



class DeviceConfigValidator:
    """ Validates peripheral config dict. """

    # Initialize logger
    extra = {"console_name":"Validator", "file_name": "validator"}
    logger = logging.getLogger(__name__)
    logger = logging.LoggerAdapter(logger, extra)


    def validate(self, config_json, filepath=False):
        """ Validates device config. Returns message on error, 
            none on success. """
        self.logger.debug("Validating ")

        # Validate json
        try:
            if filepath:
                config_dict = json.load(open(config_json))
            else:
                config_dict = json.loads(config_json)
        except json.decoder.JSONDecodeError:
            return "Invalid JSON"
        
        # Validate keys
        error_message = self.validate_keys(config_dict)
        if error_message != None:
            return error_message

        # TODO: Validate variables


    def validate_keys(self, config_dict):
        """ Validates keys in device configuration dict. """
       
        try:
            # Verify top level keys
            parent_key = ""
            config_dict["format"]
            config_dict["name"]
            config_dict["version"]
            config_dict["uuid"]
            config_dict["peripherals"]
            config_dict["controllers"]

            # Verify nested peripherals keys
            if config_dict["peripherals"] != None:
                parent_key = "peripherals "
                for peripheral in config_dict["peripherals"]:
                    peripheral["name"]
                    peripheral["uuid"]
                    peripheral["type"]
                    peripheral["parameters"]

            # Verify nested controllers keys
            if config_dict["controllers"] != None:
                parent_key = "controllers "
                for controller in config_dict["controllers"]:
                    controller["name"]
                    controller["uuid"]
                    controller["type"]
                    controller["parameters"]


        except KeyError as e:
            error_message = "Device config " + parent_key + "`{}` key is required".format(e.args[0])
            return error_message



class RecipeValidator:
    """ Validates recipe. """

    # Initialize logger
    extra = {"console_name":"Validator", "file_name": "validator"}
    logger = logging.getLogger(__name__)
    logger = logging.LoggerAdapter(logger, extra)


    def validate(self, recipe_json, filepath=False):
        """ Validates recipe. Returns message on error or None on success. """
        self.logger.info("Validating recipe")
        self.logger.warning(recipe_json)

        # Validate json
        try:
            if filepath:
                recipe_dict = json.load(open(recipe_json))
            else:
                recipe_dict = json.loads(recipe_json)
        except json.decoder.JSONDecodeError:
            return "Invalid JSON"

        # Validate format


        # Validate keys
        self.validate_keys(recipe_dict)

        # Validate recipe is parsable
        try:
            recipe_parser = RecipeParser()
            recipe_parser.parse(recipe_dict)
        except:
            error_message = "Recipe is unparsable"
            self.logger.exception(error_message)
            return error_message

        # TODO: Validate value types

        # TODO: Validate variables

        # Recipe is valid!
        return None


    def validate_uuid(self, uuid):
        """ Validates recipe uuid is not none and is unique """
        if uuid == None:
            return "Recipe UUID cannot be null"
        if RecipeModel.objects.filter(uuid=uuid).exists():
            return "Recipe UUID already exists"
        return None


    def validate_keys(self, recipe_dict):
        """ Validates keys in recipe dict. """

        try:
            # Verify top level keys
            parent_key = ""
            recipe_dict["format"]
            recipe_dict["version"]
            recipe_dict["name"]
            recipe_dict["uuid"]
            recipe_dict["parent_recipe_uuid"]
            recipe_dict["support_recipe_uuids"]
            recipe_dict["creation_timestamp_utc"]
            recipe_dict["description"]
            recipe_dict["authors"]
            recipe_dict["cultivars"]
            recipe_dict["cultivation_method"]
            recipe_dict["environments"]
            recipe_dict["phases"]
            
            # Verify nested description keys
            parent_key = "description "
            recipe_dict["description"]["breif"]
            recipe_dict["description"]["verbose"]

            # Verify nested author keys
            parent_key = "authors "
            for author in recipe_dict["authors"]:
                author["name"]
                author["email"]
                author["uuid"]

            # Verify nested cultivar keys
            parent_key = "cultivars "
            for cultivar in recipe_dict["cultivars"]:
                cultivar["name"]
                cultivar["description"]
                cultivar["uuid"]
                cultivar["link"]
                cultivar["average_height_centimeters"]
                cultivar["average_width_centimeters"]
                cultivar["average_duration_days"]
                cultivar["duration_start_stage"]

            # Verify nested cultivation method keys
            parent_key = "cultivation_method"
            recipe_dict["cultivation_method"]["name"]
            recipe_dict["cultivation_method"]["description"]
            recipe_dict["cultivation_method"]["uuid"]

        except KeyError as e:
            error_message = parent_key + "`{}` key is required".format(e.args[0])
            return error_message



