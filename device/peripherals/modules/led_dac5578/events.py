# Import standard python modules
import time, json

# Import python types
from typing import Optional, List, Dict, Any, Tuple

# Import device utilities
from device.utilities.modes import Modes

# Import peripheral event mixin
from device.peripherals.classes.peripheral.events import PeripheralEvents

# Import peripheral utilities
from device.peripherals.utilities import light

# Import driver exceptions
from device.peripherals.classes.peripheral.exceptions import DriverError

# Initialze vars
TURN_ON_EVENT = "Turn On"
TURN_OFF_EVENT = "Turn Off"
SET_CHANNEL_EVENT = "Set Channel"
FADE_EVENT = "Fade"


class LEDDAC5578Events(PeripheralEvents):  # type: ignore
    """Event mixin for led driver."""

    # Initialize var types
    mode: str
    request: Optional[Dict[str, Any]]

    def process_peripheral_specific_event(
        self, request: Dict[str, Any]
    ) -> Tuple[str, int]:
        """Processes peripheral specific events."""

        # Execute request
        if request["type"] == TURN_ON_EVENT:
            return self.process_turn_on_event()
        elif request["type"] == TURN_OFF_EVENT:
            return self.process_turn_off_event()
        elif request["type"] == SET_CHANNEL_EVENT:
            return self.process_set_channel_event(request)
        elif request["type"] == FADE_EVENT:
            return self.initialize_fade_event()
        else:
            return "Unknown event request type", 400

    def process_turn_on_event(self) -> Tuple[str, int]:
        """Processes turn on event."""
        self.logger.debug("Processing turn on event")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            return "Must be in manual mode", 400

        # Turn on driver and update reported variables
        try:
            self.driver.turn_on()
            self.update_reported_variables()
        except DriverError as e:
            self.mode = Modes.ERROR
            message = "Unable to turn on: {}".format(e)
            self.logger.debug(message)
            return message, 500
        except:
            self.mode = Modes.ERROR
            message = "Unable to turn on, unhandled exception"
            self.logger.exception(message)
            return message, 500

        # Successfully turned on
        return "Turning on", 200

    def process_turn_off_event(self) -> Tuple[str, int]:
        """Processes turn off event."""
        self.logger.debug("Processing turn off event")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            return "Must be in manual mode", 400

        # Turn off driver and update reported variables
        try:
            self.driver.turn_off()
            self.update_reported_variables()
        except DriverError as e:
            self.mode = Modes.ERROR
            message = "Unable to turn off: {}".format(e)
            self.logger.debug(message)
            return message, 500
        except:
            self.mode = Modes.ERROR
            message = "Unable to turn off, unhandled exception"
            self.logger.exception(message)
            return message, 500

        # Successfully turned off
        return "Turning off", 200

    def process_set_channel_event(self, request: Dict[str, Any]) -> Tuple[str, int]:
        """Processes set channel event."""
        self.logger.debug("Processing set channel event")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            return "Must be in manual mode", 400

        # Get request parameters
        try:
            response = request["value"].split(",")
            channel_name = str(response[0])
            percent = float(response[1])
        except KeyError as e:
            message = "Unable to set channel, invalid request parameter: {}".format(e)
            self.logger.debug(message)
            return message, 400
        except ValueError as e:
            message = "Unable to set channel, {}".format(e)
            self.logger.debug(message)
            return message, 400
        except:
            message = "Unable to set channel, unhandled exception"
            self.logger.exception(message)
            return message, 500

        # Verify channel name
        if channel_name not in self.channel_names:
            message = "Invalid channel name: {}".format(channel_name)
            self.logger.debug(message)
            return message, 400

        # Verify percent
        if percent < 0 or percent > 100:
            message = "Unable to set channel, invalid intensity: {:.0F}%".format(
                percent
            )
            self.logger.debug(message)
            return message, 400

        # Set channel and update reported variables
        try:
            self.driver.set_output(channel_name, float(percent))
            self.update_reported_variables()
        except DriverError as e:
            self.mode = Modes.ERROR
            message = "Unable to turn set channel: {}".format(e)
            self.logger.debug(message)
            return message, 500
        except:
            self.mode = Modes.ERROR
            message = "Unable to set channel, unhandled exception"
            self.logger.exception(message)
            return message, 500

        # Successfully set channel
        return "Setting {} to {:.0F}%".format(channel_name, percent), 200

    def initialize_fade_event(self) -> Tuple[str, int]:
        """Fades through all channels if no channel is specified."""
        self.logger.debug("Initializing fade event")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            return "Must be in manual mode", 400

        # Return not implemented yet
        return "Not implemented yet", 500

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
