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
SUNRISE_EVENT = "Sunrise"


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
        elif request["type"] == SUNRISE_EVENT:
            return self.sunrise()
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
        elif request["type"] == SUNRISE_EVENT:
            self._sunrise()
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

        # delay = 0.01 # too fast
        # delay = 0.05 # a bit choppy
        delay = 0.025

        # Fade up at exp(1.6)
        steps_up1 = [
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            13,
            14,
            15,
            17,
            18,
            20,
            21,
            23,
            25,
            27,
            29,
            30,
            33,
            35,
            37,
            39,
            41,
            43,
            46,
            48,
            50,
            53,
            55,
            58,
            60,
            62,
            64,
            68,
            71,
            73,
            76,
            78,
            81,
            84,
            87,
            90,
            93,
            95,
            97,
            100,
        ]
        steps_up2 = [
            0,
            1,
            3,
            5,
            7,
            9,
            11,
            13,
            15,
            17,
            20,
            22,
            24,
            27,
            30,
            33,
            36,
            39,
            43,
            46,
            49,
            53,
            56,
            60,
            64,
            68,
            72,
            76,
            80,
            84,
            88,
            93,
            97,
            100,
        ]
        steps_up3 = [
            0,
            1,
            3,
            5,
            9,
            13,
            17,
            22,
            27,
            33,
            39,
            46,
            53,
            60,
            68,
            76,
            84,
            93,
            100,
        ]

        # Group channels by type
        channels = self.manager.driver.get_channels()
        channels_by_type = {}  # dict of channel types > list
        for cname in channels:
            cdict = channels[cname]
            ctype = cdict.get("type")
            if not ctype:
                continue
            channel_list = channels_by_type.get(ctype, [])
            channel_list.append(cname)
            channels_by_type[ctype] = channel_list

        # Loop forever
        while True:

            # Get list of all channels of the same type
            for channel_type in channels_by_type:

                steps = steps_up1
                if 3 == len(channels_by_type[channel_type]):
                    steps = steps_up3
                elif 2 == len(channels_by_type[channel_type]):
                    steps = steps_up2

                # Loop up through all channels (of the same type) at same time
                for step in steps:
                    for channel_name in channels_by_type[channel_type]:

                        start_time = get_start_time()

                        # Set driver output
                        self.logger.info("Channel {}: {}%".format(channel_name, step))
                        try:
                            self.manager.driver.set_output(channel_name, step)
                        except Exception as e:
                            self.logger.exception("Unable to fade driver")
                            return

                        if not self.queue.empty():  # Check for events
                            return

                        delay_until(start_time, delay)

                # Loop down through all channels (of the same type) at same time
                for step in reversed(steps):
                    for channel_name in reversed(channels_by_type[channel_type]):

                        start_time = get_start_time()
                        # Set driver output
                        self.logger.info("Channel {}: {}%".format(channel_name, step))
                        try:
                            self.manager.driver.set_output(channel_name, step)
                        except Exception as e:
                            self.logger.exception("Unable to fade driver")
                            return

                        if not self.queue.empty():  # Check for events
                            return

                        delay_until(start_time, delay)

    def sunrise(self) -> Tuple[str, int]:
        """Pre-processes sunrise event request."""
        self.logger.debug("Pre-processing sunrise event request")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            return "Must be in manual mode", 400

        # Get channel names from config
        channel_outputs = self.manager.driver.build_channel_outputs(0)
        channel_names = channel_outputs.keys()

        # Check required channels exist in config
        required_channel_names = ["R", "FR", "WW", "CW", "G", "B"]
        for channel_name in required_channel_names:
            if channel_name not in channel_names:
                message = "Config must have channel named: {}".format(channel_name)
                return message, 500

        # Add event request to event queue
        request = {"type": SUNRISE_EVENT}
        self.queue.put(request)

        # Return not implemented yet
        return "Starting sunrise demo", 200

    def _sunrise(self) -> None:
        """Processes sunrise event request."""
        self.logger.debug("Starting sunrise demo")

        # Require mode to be in manual
        if self.mode != Modes.MANUAL:
            self.logger.critical(
                "Tried to start sunrise demo from {} mode".format(self.mode)
            )

        # Turn off channels
        try:
            self.manager.driver.turn_off()
        except Exception as e:
            self.logger.exception("Unable to run sunrise demo driver")
            return

        # Initialize sunrise properties
        delay_fast = 0.001
        pause = 0.5
        delay_fast = 0.01
        pause = 1.0
        step_delta_slow = 1
        step_delta_fast = 10
        steps_min = 0
        steps_max = 100
        channel_lists = [["FR"], ["R"], ["WW"], ["CW"]]

        # Loop forever
        while True:

            # Simulate sunrise
            for channel_list in channel_lists:

                # Set step delta
                step_delta = step_delta_fast

                # Run through all channels in list
                for channel in channel_list:

                    # Run through all steps
                    step = steps_min
                    while step <= steps_max:

                        # Set output on driver
                        message = "Setting channel {} to {}%".format(channel, step)
                        self.logger.debug(message)
                        try:
                            self.manager.driver.set_output(channel, step)
                        except Exception as e:
                            message = "Unable to set output, unhandled exception: {}".format(
                                type(e)
                            )
                            self.logger.exception(message)

                        # Increment step
                        step += step_delta

                        # Check for events
                        if not self.queue.empty():
                            return

                        # Wait delay time
                        time.sleep(delay_fast)

                    # Set step max
                    try:
                        self.manager.driver.set_output(channel, steps_max)
                    except Exception as e:
                        message = "Unable to set output, unhandled exception: {}".format(
                            type(e)
                        )
                        self.logger.exception(message)

            # Simulate noon
            time.sleep(pause)

            # Check for events
            if not self.queue.empty():
                return

            # Simulate sunset
            for channel_list in reversed(channel_lists):

                # Set step delta
                step_delta = step_delta_fast

                # Run through all channels in list
                for channel in channel_list:

                    # Run through all steps
                    step = steps_max
                    while step >= steps_min:

                        # Set output on driver
                        message = "Setting channel {} to {}%".format(channel, step)
                        self.logger.debug(message)
                        try:
                            self.manager.driver.set_output(channel, step)
                        except Exception as e:
                            message = "Unable to set output, unhandled exception: {}".format(
                                type(e)
                            )
                            self.logger.exception(message)

                        # Decrement step
                        step -= step_delta

                        # Check for events
                        if not self.queue.empty():
                            return

                        # Wait delay time
                        time.sleep(delay_fast)

                    # Set step min
                    try:
                        self.manager.driver.set_output(channel, steps_min)
                    except Exception as e:
                        message = "Unable to set output, unhandled exception: {}".format(
                            type(e)
                        )
                        self.logger.exception(message)

            # Simulate mignight
            time.sleep(pause)

            # Check for events
            if not self.queue.empty():
                return


def get_start_time() -> float:
    return time.time()


def delay_until(start_time: float, delay: float) -> None:
    now = time.time()
    if now - start_time < delay:
        time.sleep(delay - (now - start_time))
    return
