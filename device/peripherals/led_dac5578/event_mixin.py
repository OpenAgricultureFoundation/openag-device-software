# Import device utilities
from device.utilities.modes import Modes
from device.utilities.error import Error

# Import peripheral event mixin
from device.peripherals.classes.event_mixin import PeripheralEventMixin


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
        # elif request["type"] == "Fade Concurrently":
        #     self.process_fade_concurrently_event()
        # elif request["type"] == "Fade Sequentially":
        #     self.process_fade_sequentially_event()
        # elif request["type"] == "Turn On Channel":
        #     self.response = self.process_turn_on_channel_event(request)
        # elif request["type"] == "Turn Off Channel":
        #     self.response = self.process_turn_off_channel_event(request)
        # elif request["type"] == "Fade Channel":
        #     self.process_fade_channel_event(request)
        # elif request["type"] == "Set Channel Output":
        #     self.response = self.process_set_channel_output_event(request)
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
            return response
        except Exception as e:
            self.error = "Unable to turn light off"
            self.logger.exception(self.error)
            response = {"status": 500, "message": self.error}
            self.mode = Modes.ERROR
            return response


    # def process_fade_concurrently_event(self):
    #     """ Processes fade concurrently event. """
    #     self.logger.debug("Processing fade concurrently event")

    #     # Require mode to be in manual
    #     if self.mode != Modes.MANUAL:
    #         self.response = {"status": 400, "message": "Must be in manual mode."}
    #         return

    #     # Return response to event request
    #     self.response = {"status": 200, "message": "Fading concurrently!"}

    #     # Start fade concurrently loop, exits on new event
    #     try:
    #         self.fade_concurrently()
    #     except:
    #         self.error = "Fade concurrently failed"
    #         self.logger.exception(self.error)
    #         self.mode = Modes.ERROR


    # def process_fade_sequentially_event(self):
    #     """ Processes fade sequentially event. """
    #     self.logger.debug("Processing fade sequentially event")

    #     # Require mode to be in manual
    #     if self.mode != Modes.MANUAL:
    #         self.response = {"status": 400, "message": "Must be in manual mode."}
    #         return

    #     # Return response to event request
    #     self.response = {"status": 200, "message": "Fading sequentially!"}

    #     # Start fade concurrently loop, exits on new event
    #     try:
    #         self.fade_sequentially()
    #     except:
    #         self.error = "Fade sequentially failed"
    #         self.logger.exception(self.error)
    #         self.mode = Modes.ERROR
    #         return


    # def process_turn_on_channel_event(self, request):
    #     """ Processes turn off event. """
    #     self.logger.debug("Processing turn on channel event")

    #     # Require mode to be in manual
    #     if self.mode != Modes.MANUAL:
    #         response = {"status": 400, "message": "Must be in manual mode."}
    #         return response

    #     # Verify value in request
    #     try:
    #         channel_name = request["value"]
    #     except KeyError as e:
    #         self.logger.exception("Invalid request parameters")
    #         response = {"status": 400, "message": "Invalid request parameters: {}".format(e)}
    #         return response

    #     # Check channel name in channel outputs
    #     if channel_name not in self.channel_outputs.keys():
    #         response = {"status": 400, "message": "Invalid channel name."}
    #         return response

    #     # Execute request
    #     try:
    #         self.turn_on_channel_output(channel_name)
    #         response = {"status": 200, "message": "Turned light channel `{}` on!".format(channel_name)}
    #         return response
    #     except Exception as e:
    #         self.error = "Unable to turn light channel `{}` on".format(channel_name)
    #         self.logger.exception(self.error)
    #         self.mode = Modes.ERROR
    #         response = {"status": 500, "message": self.error}
    #         return response


    # def process_turn_off_channel_event(self, request):
    #     """ Processes turn off channel event. """
    #     self.logger.debug("Processing turn off channel event")

    #     # Require mode to be in manual
    #     if self.mode != Modes.MANUAL:
    #         response = {"status": 400, "message": "Must be in manual mode."}
    #         return response

    #     # Verify value in request
    #     try:
    #         channel_name = request["value"]
    #     except KeyError as e:
    #         self.logger.exception("Invalid request parameters")
    #         response = {"status": 400, "message": "Invalid request parameters: {}".format(e)}
    #         return response

    #     # Check channel name in channel outputs
    #     if channel_name not in self.channel_outputs.keys():
    #         response = {"status": 400, "message": "Invalid channel name."}
    #         return response

    #     # Execute request
    #     try:
    #         self.turn_off_channel_output(channel_name)
    #         response = {"status": 200, "message": "Turned light channel `{}` off!".format(channel_name)}
    #         return response
    #     except Exception as e:
    #         self.error = "Unable to turn light channel `{}` off".format(channel_name)
    #         self.logger.exception(self.error)
    #         self.mode = Modes.ERROR
    #         response = {"status": 500, "message": self.error}
    #         return response


    # def process_fade_channel_event(self, request):
    #     """ Processes fadef channel event. """
    #     self.logger.debug("Processing fade channel event")

    #     # Require mode to be in manual
    #     if self.mode != Modes.MANUAL:
    #         self.response = {"status": 400, "message": "Must be in manual mode."}
    #         return

    #     # Verify value in request
    #     try:
    #         channel_name = request["value"]
    #     except KeyError as e:
    #         self.logger.exception("Invalid request parameters")
    #         self.response = {"status": 400, "message": "Invalid request parameters: {}".format(e)}
    #         return

    #     # Check channel name in channel outputs
    #     if channel_name not in self.channel_outputs.keys():
    #         self.response = {"status": 400, "message": "Invalid channel name."}
    #         return

    #     # Return response to event request
    #     self.response = {"status": 200, "message": "Fading channel!"}

    #     # Execute request
    #     try:
    #         self.fade_channel_output(channel_name)
    #         self.response = {"status": 200, "message": "Fading channel `{}`!".format(channel_name)}
    #         return
    #     except Exception as e:
    #         self.error = "Unable to fade channel `{}`".format(channel_name)
    #         self.logger.exception(self.error)
    #         self.mode = Modes.ERROR
    #         self.response = {"status": 500, "message": self.error}
    #         return


    # def process_set_channel_output_event(self, request):
    #     """ Processes turn off event. """
    #     self.logger.debug("Processing set channel output event")

    #     # Require mode to be in manual
    #     if self.mode != Modes.MANUAL:
    #         response = {"status": 400, "message": "Must be in manual mode."}
    #         return response

    #     # Verify value in request
    #     try:
    #         channel_name, output_percent = request["value"].split(",")
    #         self.logger.debug("channel_name = {}".format(channel_name))
    #         output_percent = float(output_percent)
    #         self.logger.debug("output_percent = {}".format(output_percent))
    #     except KeyError as e:
    #         self.logger.exception("Invalid request parameters")
    #         response = {"status": 400, "message": "Invalid request parameters: {}".format(e)}
    #         return response

    #     # Check channel name in channel outputs
    #     if channel_name not in self.channel_outputs.keys():
    #         response = {"status": 400, "message": "Invalid channel name."}
    #         return response

    #     # Check valid channel output percent
    #     if output_percent < 0 or output_percent > 100:
    #         response = {"status": 400, "message": "Invalid channel name."}
    #         return response

    #     # Execute request
    #     try:
    #         self.set_channel_output(channel_name, output_percent)
    #         response = {"status": 200, "message": "Set light channel `{}` to {}%!".format(channel_name, output_percent)}
    #         return response
    #     except Exception as e:
    #         self.error = "Unable to turn light channel `{}` to {}%".format(channel_name, output_percent)
    #         self.logger.exception(self.error)
    #         self.mode = Modes.ERROR
    #         response = {"status": 500, "message": self.error}
    #         return response