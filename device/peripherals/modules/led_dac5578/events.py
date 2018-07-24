# Import standard python modules
from typing import Optional, Tuple, List, Dict
import time, json

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.error import Error

# Import peripheral event mixin
from device.peripherals.classes.peripheral_events import PeripheralEvents

# Import peripheral utilities
from device.peripherals.utilities import light


class LEDDAC5578Events(PeripheralEvents):
    """ Event mixin for led array. """

    def process_peripheral_specific_event(self, request):
        """ Processes peripheral specific event event. Gets request parameters, 
            executes request, returns response. """

        # Execute request
        if request["type"] == "Turn On":
            self.response = self.process_turn_on_event()
        elif request["type"] == "Turn Off":
            self.response = self.process_turn_off_event()
        elif request["type"] == "Set Channel":
            self.response = self.process_set_channel_event(request)
        elif request["type"] == "Fade":
            self.response = self.initialize_fade_event()
            self.fade()
        elif request["type"] == "Calculate ULRF From Percents":
            self.response = self.process_calculate_ulrf_from_percents(request)
        elif request["type"] == "Calculate ULRF From Watts":
            self.response = self.process_calculate_ulrf_from_watts(request)
        else:
            message = "Unknown event request type!"
            self.logger.info(message)
            self.response = {"status": 400, "message": message}

    def process_turn_on_event(self):
        """ Processes turn on event. """
        self.logger.debug("Processing turn on event")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            response = {"status": 400, "message": "Must be in manual mode."}
            return response

        # Turn on array and update reported variables
        error = self.array.turn_on()
        self.update_reported_variables()

        # Check for errors
        if error.exists():
            self.mode = Modes.ERROR
            response = {"status": 400, "message": error.trace}
            return response

        # Successfully turned on!
        response = {"status": 200, "message": "Turned on!"}
        return response

    def process_turn_off_event(self):
        """ Processes turn off event. """
        self.logger.debug("Processing turn off event")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            response = {"status": 400, "message": "Must be in manual mode."}
            return response

        # Turn off array and update reported variables
        error = self.array.turn_off()
        self.update_reported_variables()

        # Check for errors
        if error.exists():
            self.mode = Modes.ERROR
            response = {"status": 400, "message": error.trace}
            return response

        # Successfully turned on!
        response = {"status": 200, "message": "Turned off!"}
        return response

    def process_set_channel_event(self, request) -> None:
        """ Processes set channel event. """
        self.logger.debug("Processing set channel event")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            response = {"status": 400, "message": "Must be in manual mode."}
            return response

        # Verify request parameters
        try:
            channel_name, percent = request["value"].split(",")
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            return {"status": 400, "message": "Invalid request parameter: " + str(e)}

        # Set channel and update reported variables
        error = self.array.set_output(channel_name, float(percent))
        self.update_reported_variables()

        # Check for errors
        if error.exists():
            self.mode = Modes.ERROR
            response = {"status": 400, "message": error.trace}
            return response

        # Successfully turned on!
        response = {"status": 200, "message": "Turned on!"}
        return response

    def initialize_fade_event(self) -> Dict:
        """ Fades through all channels if no channel is specified. """
        self.logger.debug("Initializing fade event")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            response = {"status": 400, "message": "Must be in manual mode."}
            return response

        # Successfully initialized fade event!
        response = {"status": 200, "message": "Fading!"}
        return response

    def fade(self, channel_name: Optional[str] = None):
        """ Fades through channel names. """
        self.logger.debug("Fading")

        # Turn off channels
        error = self.array.turn_off()

        # Check for errors
        if error.exists():
            error.report("Unable to fade array")
            return error

        # Set channel or channels
        if channel_name != None:
            channel_names = [channel_name]
        else:
            channel_outputs = self.array.build_channel_outputs(0)
            channel_names = channel_outputs.keys()

        # Loop forever
        while True:

            # Loop through all channels
            for channel_name in channel_names:

                # Fade up
                for value in range(0, 100, 10):

                    # Set array output
                    self.logger.info("Channel {}: {}%".format(channel_name, value))
                    error = self.array.set_output(channel_name, value)

                    # Check for errors
                    if error.exists():
                        error.report("Unable to fade array")
                        self.logger.error(error.trace)
                        self.mode = Modes.ERROR
                        return

                    # Check for new events
                    if self.request != None:
                        request = self.request
                        self.request = None
                        self.process_event(request)
                        return

                    # Check for new modes
                    if self.mode != Modes.MANUAL:
                        return

                    # Update every 100ms
                    time.sleep(0.1)

                # Fade down
                for value in range(100, 0, -10):

                    # Set array output
                    self.logger.info("Channel {}: {}%".format(channel_name, value))
                    error = self.array.set_output(channel_name, value)

                    # Check for errors
                    if error.exists():
                        error.report("Unable to fade array")
                        self.logger.error(error.trace)
                        self.mode = Modes.ERROR
                        return

                    # Check for new events
                    if self.request != None:
                        request = self.request
                        self.request = None
                        self.process_event(request)
                        return

                    # Check for new modes
                    if self.mode != Modes.MANUAL:
                        return

                    # Update every 100ms
                    time.sleep(0.1)

    def process_calculate_ulrf_from_percents(self, request) -> Dict:
        """Processes calculating universal light recipe format (ULRF) parameters 
        from channel power percents."""
        self.logger.debug("Processing calculating ULRF from percents")

        # Verify request parameters
        try:
            data = json.loads(request["value"])
            channel_power_percents = data["channel_power_percents"]
            illumination_distance = data["illumination_distance_cm"]
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            return {"status": 400, "message": "Invalid request parameter: " + str(e)}

        # Calculate light urf parameters
        try:
            spectrum, ppfd, distance = light.calculate_ulrf_from_percents(
                channel_configs=self.channel_configs,
                channel_power_percents=channel_power_percents,
                distance=illumination_distance,
            )
            return {
                "status": 200,
                "message": "Successfully calculated!",
                "spectrum_nm_percents": spectrum,
                "ppfd_umol_m2_s": ppfd,
                "illumination_distance_cm": distance,
            }
        except Exception as e:  # TODO: Break out exception types
            self.logger.exception("Unable to calculate light urf from percents")
            return {"status": 500, "message": str(e)}
