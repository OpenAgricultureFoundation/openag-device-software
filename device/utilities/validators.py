# Import standard python modules
import json, logging

# Import device parsers
from device.utilities.parsers import RecipeParser

# Import app models
from app.models import RecipeModel


class RecipeValidator:
    """ Validates recipe. """

    # Initialize logger
    extra = {"console_name":"Recipe", "file_name": "device"}
    logger = logging.getLogger(__name__)
    logger = logging.LoggerAdapter(logger, extra)


    def validate(self, recipe_json):
        """ Validates recipe. Returns message on error or None on success. """
        self.logger.info("Validating recipe")
            
        # Initialize parsed recipe dict    
        parsed_recipe = {}

        # Validate json
        try:
            recipe_dict = json.loads(recipe_json)
        except json.decoder.JSONDecodeError:
            return "Invalid JSON"

        # Validate keys
        error_message = self.validate_keys(recipe_dict)
        if error_message != None:
            return error_message

        # Validate recipe is parsable
        try:
            recipe_parser = RecipeParser()
            recipe_parser.parse(recipe_dict)
        except:
            error_message = "Recipe is unparsable"
            self.logger.exception(error_message)
            return error_message


        # Validate recipe uuid is not none and is unique
        error_message = self.validate_uuid(recipe_dict["uuid"])
        if error_message != None:
            return error_message

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





        