# Import python types
from typing import Dict

# Import device utilities
from device.utilities.modes import Modes


class CoordinatorEvents:
    """Event mixin for coordinator manager."""

    def process_event(self, request: Dict) -> None:
        """Processes an event request."""

        # Get request parameters
        try:
            request_type = request["type"]
        except KeyError as e:
            message = "Invalid request parameters: {}".format(e)
            self.logger.exception(message)
            self.response = {"status": 400, "message": message}
            return

        # Execute request
        if request_type == "Load Recipe":
            self.process_load_recipe_event()
        elif request_type == "Start Recipe":
            self.process_start_recipe_event(request)
        elif request_type == "Stop Recipe":
            self.process_stop_recipe_event()
        elif request_type == "Reset":
            self.process_reset_event()
        elif request_type == "Load Config":
            self.process_load_config_event(request)
        else:
            message = "Received invalid event request type: {}".format(request_type)
            self.logger.info(message)

    def process_load_recipe_event(self):
        """Processes load recipe event."""
        self.logger.critical("Loading recipe")
        self.response = {"status": 500, "message": "Not implemented yet"}

    # Also called from the IoTManager command receiver.
    # Need to save the json recipe to the DB first
    # (referenced here by UUID)
    def process_start_recipe_event(self, request: Dict) -> None:
        """Processes load recipe event."""
        self.logger.debug("Processing start recipe event")

        # TODO: Check for valid mode transition

        # For backwards compatibility with SW v0.1.0
        if type(request) == str:
            request_uuid = request
            request_timestamp = None
        else:
            # Get recipe uuid value and timestamp:
            self.logger.info("request = {}".format(request))
            request_uuid = request.get("uuid", None)
            request_timestamp = request.get("timestamp", None)

        # Verify uuid value exists
        if request_uuid == None:
            message = "Invalid request parameters: `uuid`"
            self.response = {"status": 400, "message": message}
            return

        # Check if starting recipe at timestamp
        if request_timestamp != None:

            # Check timestamp is in the future
            if request_timestamp < time.time():
                message = "Invalid timestamp, value must be in the future"
                self.response = {"status": 400, "message": message}
                return

            # Convert timestamp in seconds to minutes
            request_timestamp_minutes = int(request_timestamp / 60.0)
        else:
            request_timestamp_minutes = None

        # Send start recipe command to recipe thread
        self.recipe.commanded_recipe_uuid = request_uuid
        self.recipe.commanded_start_timestamp_minutes = request_timestamp_minutes
        self.recipe.commanded_mode = Modes.START

        # Set response
        self.response = {"status": 200, "message": "Starting recipe"}

    # Also called from the IoTManager command receiver.
    def process_stop_recipe_event(self):
        """Processes load recipe event."""
        self.logger.debug("Processing stop recipe event")

        # TODO: Check for valid mode transition

        # Send stop recipe command
        self.recipe.commanded_mode = Modes.STOP

        # Wait for recipe to be picked up by recipe thread or timeout event
        start_time_seconds = time.time()
        timeout_seconds = 10
        while True:
            # Exit when recipe thread transitions to NORECIPE
            if self.recipe.mode == Modes.NORECIPE:
                self.response = {"status": 200, "message": "Stopped recipe"}
                break

            # Exit on timeout
            if time.time() - start_time_seconds > timeout_seconds:
                self.logger.critical(
                    "Unable to stop recipe within 10 seconds. Something is wrong with code."
                )
                self.response = {
                    "status": 500,
                    "message": "Unable to stop recipe, thread did not change state withing 10 seconds. Something is wrong with code.",
                }
                break

    def process_reset_event(self):
        """ Processes reset event. """
        self.logger.debug("Processing reset event")
        self.response = {"status": 200, "message": "Pretended to reset device"}

    def process_load_config_event(self, request):
        """ Processes load config event. """
        self.logger.debug("Processing load config event")

        # Get request parameters
        config_uuid = request.get("uuid", None)
        self.logger.debug("Received config_uuid: {}".format(config_uuid))

        # TODO: This flow is a bit wonky...clean up idea on uuid vs. filename

        # Get filename of corresponding uuid
        config_filename = None
        for filepath in glob.glob("data/devices/*.json"):
            device_config = json.load(open(filepath))
            if device_config["uuid"] == config_uuid:
                config_filename = filepath.split("/")[-1].replace(".json", "")

        # Verify valid config uuid
        if config_filename == None:
            message = "Invalid config uuid, corresponding filepath not found"
            self.response = {"status": 400, "message": message}
            return

        # Write config filename to to device config path
        with open(DEVICE_CONFIG_PATH, "w") as f:
            f.write(config_filename + "\n")

        # Transition to config mode
        self.mode = Modes.CONFIG

        # Return success response
        message = "Loading config: {}".format(config_filename)
        self.response = {"status": 200, "message": message}
