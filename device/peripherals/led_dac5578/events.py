# Import standard python modules
from typing import Optional, Tuple, List, Dict
import time

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.error import Error

# Import peripheral event mixin
from device.peripherals.classes.event_mixin import PeripheralEventMixin


class EventMixin(PeripheralEventMixin):
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
            self.response = self.initialize_fade_event()
            self.fade()
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

        # Turn off array
        error = self.array.turn_off()

        # Check for errors
        if error.exists():
            self.mode = Modes.ERROR
            response = {"status": 400, "message": error.trace}
            return response

        # Successfully turned on!
        response = {"status": 200, "message": "Turned off!"}
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
