# Import device utilities
from device.utilities.modes import Modes
from device.utilities.error import Error

# Import peripheral event mixin
from device.peripherals.classes.event_mixin import PeripheralEventMixin


# TODO: Error handle from these functions


class LEDEventMixin(PeripheralEventMixin):
    """ Event mixin for led array. """


    def process_peripheral_specific_event(self, request):
        """ Processes peripheral specific event event. Gets request parameters, 
            executes request, returns response. """

        # Execute request
        if request["type"] == "Turn On":
            self.response = self.process_turn_on_event()
        elif request["type"] == "Turn Off":
            self.response = self.process_turn_off_event()
        elif request["type"] == "Fade":
            self.response = self.process_fade_event()
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

        # Execute request
        try:
            self.array.turn_on()
            response = {"status": 200, "message": "Turned light on!"}
            return response
        except Exception as e:
            self.error = "Unable to turn light on"
            self.logger.exception(self.error)
            response = {"status": 500, "message": self.error}
            self.mode = Modes.ERROR
            return response


    def process_turn_off_event(self):
        """ Processes turn off event. """
        self.logger.debug("Processing turn off event")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            response = {"status": 400, "message": "Must be in manual mode."}
            return response

        # Execute request
        try:
            self.array.turn_off()
            response = {"status": 200, "message": "Turned light off!"}
            self.logger.debug("response = {}".format(response))
            return response
        except Exception as e:
            self.error = "Unable to turn light off"
            self.logger.exception(self.error)
            response = {"status": 500, "message": self.error}
            self.mode = Modes.ERROR
            return response


    def process_fade_event(self):
        """ Processes fade event. """
        self.logger.debug("Processing fade event")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            response = {"status": 400, "message": "Must be in manual mode."}
            return response

        # Execute request
        try:
            self.array.fade(10)
            response = {"status": 200, "message": "Started fading lights!"}
            self.logger.debug("response = {}".format(response))
            return response
        except Exception as e:
            self.error = "Unable to fade lights"
            self.logger.exception(self.error)
            response = {"status": 500, "message": self.error}
            self.mode = Modes.ERROR
            return response
