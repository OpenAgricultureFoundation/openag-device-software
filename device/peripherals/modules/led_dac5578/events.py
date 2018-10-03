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
    """Peripheral event handler."""

    # Initialize var types
    mode: str
    request: Optional[Dict[str, Any]]

    def create_peripheral_specific_event(
        self, request: Dict[str, Any]
    ) -> Tuple[str, int]:
        """Processes peripheral specific event."""
        if request["type"] == TURN_ON_EVENT:
            return self.turn_on()
        elif request["type"] == TURN_OFF_EVENT:
            return self.turn_off()
        elif request["type"] == SET_CHANNEL_EVENT:
            return self.set_channel(request)
        elif request["type"] == FADE_EVENT:
            return self.fade()
        else:
            return "Unknown event request type", 400

    def check_peripheral_specific_events(self, request: Dict[str, Any]) -> None:
        """Checks peripheral specific events."""
        if request["type"] == TURN_ON_EVENT:
            self._turn_on()
        elif request["type"] == TURN_OFF_EVENT:
            self._turn_off()
        elif request["type"] == SET_CHANNEL_EVENT:
            self._set_channel(request)
        elif request["type"] == FADE_EVENT:
            self._fade()
        else:
            message = "Invalid event request type in queue: {}".format(request["type"])
            self.logger.error(message)

    def turn_on(self) -> Tuple[str, int]:
        """Pre-processes turn on event request."""
        self.logger.debug("Pre-processing turn on event request")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            return "Must be in manual mode", 400

        # Add event request to event queue
        request = {"type": TURN_ON_EVENT}
        self.queue.put(request)

        # Successfully turned on
        return "Turning on", 200

    def _turn_on(self) -> None:
        """Processes turn on event request."""
        self.logger.debug("Processing turn on event request")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            self.logger.critical("Tried to turn on from {} mode".format(self.mode))

        # Turn on driver and update reported variables
        try:
            self.manager.channel_setpoints = self.manager.driver.turn_on()
            self.manager.update_reported_variables()
        except DriverError as e:
            self.mode = Modes.ERROR
            message = "Unable to turn on: {}".format(e)
            self.logger.debug(message)
        except:
            self.mode = Modes.ERROR
            message = "Unable to turn on, unhandled exception"
            self.logger.exception(message)

    def turn_off(self) -> Tuple[str, int]:
        """Pre-processes turn off event request."""
        self.logger.debug("Pre-processing turn off event request")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            return "Must be in manual mode", 400

        # Add event request to event queue
        request = {"type": TURN_OFF_EVENT}
        self.queue.put(request)

        # Successfully turned off
        return "Turning off", 200

    def _turn_off(self) -> None:
        """Processes turn off event request."""
        self.logger.debug("Processing turn off event request")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            self.logger.critical("Tried to turn off from {} mode".format(self.mode))

        # Turn off driver and update reported variables
        try:
            self.manager.channel_setpoints = self.manager.driver.turn_off()
            self.manager.update_reported_variables()
        except DriverError as e:
            self.mode = Modes.ERROR
            message = "Unable to turn off: {}".format(e)
            self.logger.debug(message)
        except:
            self.mode = Modes.ERROR
            message = "Unable to turn off, unhandled exception"
            self.logger.exception(message)

    def set_channel(self, request: Dict[str, Any]) -> Tuple[str, int]:
        """Pre-processes set channel event request."""
        self.logger.debug("Pre-processing set channel event request")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            message = "Must be in manual mode"
            self.logger.debug(message)
            return message, 400

        # Get request parameters
        try:
            response = request["value"].split(",")
            channel = str(response[0])
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
        if channel not in self.manager.channel_names:
            message = "Invalid channel name: {}".format(channel)
            self.logger.debug(message)
            return message, 400

        # Verify percent
        if percent < 0 or percent > 100:
            message = "Unable to set channel, invalid intensity: {:.0F}%".format(
                percent
            )
            self.logger.debug(message)
            return message, 400

        # Add event request to event queue
        request = {"type": SET_CHANNEL_EVENT, "channel": channel, "percent": percent}
        self.queue.put(request)

        # Return response
        return "Setting {} to {:.0F}%".format(channel, percent), 200

    def _set_channel(self, request: Dict[str, Any]) -> None:
        """Processes set channel event request."""
        self.logger.debug("Processing set channel event")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            self.logger.critical("Tried to set channel from {} mode".format(self.mode))

        # Get channel and percent
        channel = request.get("channel")
        percent = float(request.get("percent"))  # type: ignore

        # Set channel and update reported variables
        try:
            self.manager.driver.set_output(channel, percent)
            self.manager.channel_setpoints[channel] = percent
            self.manager.update_reported_variables()
        except DriverError as e:
            self.mode = Modes.ERROR
            message = "Unable to set channel: {}".format(e)
            self.logger.debug(message)
        except:
            self.mode = Modes.ERROR
            message = "Unable to set channel, unhandled exception"
            self.logger.exception(message)

    def fade(self) -> Tuple[str, int]:
        """Pre-processes fade event request."""
        self.logger.debug("Pre-processing fade event request")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            return "Must be in manual mode", 400

        # Add event request to event queue
        request = {"type": FADE_EVENT}
        self.queue.put(request)

        # Return not implemented yet
        return "Fading", 200

    def _fade(self, channel_name: Optional[str] = None) -> None:
        """Processes fade event request."""
        self.logger.debug("Fading")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            self.logger.critical("Tried to fade from {} mode".format(self.mode))

        # Turn off channels
        try:
            self.manager.driver.turn_off()
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
                        self.manager.driver.set_output(channel_name, value)
                    except Exception as e:
                        self.logger.exception("Unable to fade driver")
                        return

                    # Check for events
                    if not self.queue.empty():
                        break

                    # Update every 100ms
                    time.sleep(0.1)

                # Fade down
                for value in range(100, 0, -10):

                    # Set driver output
                    self.logger.info("Channel {}: {}%".format(channel_name, value))
                    try:
                        self.manager.driver.set_output(channel_name, value)
                    except Exception as e:
                        self.logger.exception("Unable to fade driver")
                        return

                    # Check for events
                    if not self.queue.empty():
                        break

                    # Update every 100ms
                    time.sleep(0.1)
