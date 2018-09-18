# Import standard python modules
import time, json

# Import python types
from typing import Optional, List, Dict, Any

# Import device utilities
from device.utilities.modes import Modes

# Import peripheral event mixin
from device.peripherals.classes.peripheral.events import PeripheralEvents

# Import peripheral utilities
from device.peripherals.utilities import light


class LEDDAC5578Events(PeripheralEvents):  # type: ignore
    """Event mixin for led driver."""

    # Initialize var types
    mode: str
    request: Optional[Dict[str, Any]]

    def process_peripheral_specific_event(self, request: Dict[str, Any]) -> None:
        """Processes peripheral specific event event. Gets request parameters, 
        executes request, returns response."""

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
            message = "Unknown event request type"
            self.logger.info(message)
            self.response = {"status": 400, "message": message}

    def process_turn_on_event(self) -> Dict[str, Any]:
        """Processes turn on event."""
        self.logger.debug("Processing turn on event")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            return {"status": 400, "message": "Must be in manual mode."}

        # Turn on driver and update reported variables
        try:
            self.driver.turn_on()
            self.update_reported_variables()
        except Exception as e:
            self.mode = Modes.ERROR
            message = "Unable to turn on: {}".format(e)
            return {"status": 400, "message": message}

        # Successfully turned on
        return {"status": 200, "message": "Turned on"}

    def process_turn_off_event(self) -> Dict[str, Any]:
        """Processes turn off event."""
        self.logger.debug("Processing turn off event")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            return {"status": 400, "message": "Must be in manual mode."}

        # Turn off driver and update reported variables
        try:
            self.driver.turn_off()
            self.update_reported_variables()
        except Exception as e:
            self.mode = Modes.ERROR
            message = "Unable to turn off: {}".format(e)
            return {"status": 400, "message": message}

        # Successfully turned off
        return {"status": 200, "message": "Turned off"}

    def process_set_channel_event(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Processes set channel event."""
        self.logger.debug("Processing set channel event")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            return {"status": 400, "message": "Must be in manual mode."}

        # Verify request parameters
        try:
            channel_name, percent = request["value"].split(",")
        except KeyError as e:
            self.logger.exception("Invalid request parameters")
            return {"status": 400, "message": "Invalid request parameter: " + str(e)}

        # Set channel and update reported variables
        try:
            self.driver.set_output(channel_name, float(percent))
            self.update_reported_variables()
        except Exception as e:
            self.mode = Modes.ERROR
            message = "Unable to set channel: {}".format(e)
            return {"status": 400, "message": message}

        # Successfully turned on
        return {"status": 200, "message": "Turned on"}

    def initialize_fade_event(self) -> Dict[str, Any]:
        """Fades through all channels if no channel is specified."""
        self.logger.debug("Initializing fade event")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            return {"status": 400, "message": "Must be in manual mode."}

        # Successfully initialized fade event
        return {"status": 200, "message": "Fading"}

    def fade(self, channel_name: Optional[str] = None) -> None:
        """Fades through channel names."""
        self.logger.debug("Fading")

        # Turn off channels
        try:
            self.driver.turn_off()
        except Exception as e:
            self.logger.exception("Unable to fade driver")
            return

        # Set channel or channels
        if channel_name != None:
            channel_names = [channel_name]
        else:
            channel_outputs = self.driver.build_channel_outputs(0)
            channel_names = channel_outputs.keys()

        # Loop forever
        while True:

            # Loop through all channels
            for channel_name in channel_names:

                # Fade up
                for value in range(0, 100, 10):

                    # Set driver output
                    self.logger.info("Channel {}: {}%".format(channel_name, value))
                    try:
                        self.driver.set_output(channel_name, value)
                    except Exception as e:
                        self.logger.exception("Unable to fade driver")
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

                    # Set driver output
                    self.logger.info("Channel {}: {}%".format(channel_name, value))
                    try:
                        self.driver.set_output(channel_name, value)
                    except Exception as e:
                        self.logger.exception("Unable to fade driver")
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
