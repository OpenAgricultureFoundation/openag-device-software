# Import standard python modules
import threading, time

# Import python types
from typing import Optional, Tuple, Dict, Any

# Import device utilities
from device.utilities import maths

# Import peripheral utilities
from device.peripherals.utilities import light

# Import manager elements
from device.peripherals.classes.peripheral import manager, modes
from device.peripherals.modules.led_dac5578 import driver, exceptions, events


class LEDDAC5578Manager(manager.PeripheralManager):
    """Manages an LED driver controlled by a dac5578."""

    prev_desired_intensity: Optional[float] = None
    prev_desired_spectrum: Optional[Dict[str, float]] = None
    prev_desired_distance: Optional[float] = None
    prev_heartbeat_time: float = 0
    heartbeat_interval: float = 60  # seconds -> every minute
    prev_reinit_time: float = 0
    reinit_interval: float = 300  # seconds -> every 5 minutes

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize light driver."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize panel and channel configs
        self.panel_configs = self.communication.get("panels")
        self.panel_properties = self.setup_dict.get("properties")

        # Initialize variable names
        self.intensity_name = self.variables["sensor"]["ppfd_umol_m2_s"]
        self.spectrum_name = self.variables["sensor"]["spectrum_nm_percent"]
        self.distance_name = self.variables["sensor"]["illumination_distance_cm"]
        self.channel_setpoints_name = self.variables["actuator"][
            "channel_output_percents"
        ]

        # Parse panel properties
        self.channel_types = self.panel_properties.get(  # type: ignore
            "channel_types", {}
        )
        channels = self.panel_properties.get("channels", {})  # type: ignore
        self.channel_names = channels.keys()

    @property
    def spectrum(self) -> Any:
        """Gets spectrum value."""
        return self.state.get_peripheral_reported_sensor_value(
            self.name, self.spectrum_name
        )

    @spectrum.setter
    def spectrum(self, value: Optional[Dict[str, float]]) -> None:
        """Sets spectrum value in shared state."""
        self.state.set_peripheral_reported_sensor_value(
            self.name, self.spectrum_name, value
        )
        self.state.set_environment_reported_sensor_value(
            self.name, self.spectrum_name, value, simple=True
        )

    @property
    def desired_spectrum(self) -> Any:
        """Gets desired spectrum value from shared environment state if not 
        in manual mode, otherwise gets it from peripheral state."""
        if self.mode != modes.MANUAL:
            return self.state.get_environment_desired_sensor_value(self.spectrum_name)
        else:
            return self.state.get_peripheral_desired_sensor_value(
                self.name, self.spectrum_name
            )

    @property
    def intensity(self) -> Optional[float]:
        """Gets intensity value."""
        value = self.state.get_peripheral_reported_sensor_value(
            self.name, self.intensity_name
        )
        if value != None:
            return float(value)
        return None

    @intensity.setter
    def intensity(self, value: float) -> None:
        """Sets intensity value in shared state."""
        self.state.set_peripheral_reported_sensor_value(
            self.name, self.intensity_name, value
        )
        self.state.set_environment_reported_sensor_value(
            self.name, self.intensity_name, value, simple=True
        )

    @property
    def desired_intensity(self) -> Optional[float]:
        """Gets desired intensity value from shared environment state if not 
        in manual mode, otherwise gets it from peripheral state."""
        if self.mode != modes.MANUAL:
            value = self.state.get_environment_desired_sensor_value(self.intensity_name)
            if value != None:
                return float(value)
            return None
        else:
            value = self.state.get_peripheral_reported_sensor_value(
                self.name, self.intensity_name
            )
            if value != None:
                return float(value)
            return None

    @property
    def distance(self) -> Optional[float]:
        """Gets distance value."""
        value = self.state.get_peripheral_reported_sensor_value(
            self.name, self.distance_name
        )
        if value != None:
            return float(value)
        return None

    @distance.setter
    def distance(self, value: float) -> None:
        """Sets distance value in shared state."""
        self.state.set_peripheral_reported_sensor_value(
            self.name, self.distance_name, value
        )
        self.state.set_environment_reported_sensor_value(
            self.name, self.distance_name, value, simple=True
        )

    @property
    def desired_distance(self) -> Optional[float]:
        """Gets desired distance value from shared environment state if not 
        in manual mode, otherwise gets it from peripheral state."""
        if self.mode != modes.MANUAL:
            value = self.state.get_environment_desired_sensor_value(self.distance_name)
            if value != None:
                return float(value)
            return None
        else:
            value = self.state.get_peripheral_reported_sensor_value(
                self.name, self.distance_name
            )
            if value != None:
                return float(value)
            return None

    @property
    def channel_setpoints(self) -> Any:
        """Gets channel setpoints value."""
        return self.state.get_peripheral_reported_actuator_value(
            self.name, self.channel_setpoints_name
        )

    @channel_setpoints.setter
    def channel_setpoints(self, value: Dict[str, float]) -> None:
        """ Sets channel outputs value in shared state. """
        self.state.set_peripheral_reported_actuator_value(
            self.name, self.channel_setpoints_name, value
        )
        self.state.set_environment_reported_actuator_value(
            self.channel_setpoints_name, value
        )

    @property
    def desired_channel_setpoints(self) -> Any:
        """ Gets desired distance value from shared environment state if not 
            in manual mode, otherwise gets it from peripheral state. """
        if self.mode != modes.MANUAL:
            return self.state.get_environment_desired_actuator_value(
                self.channel_setpoints_name
            )
        else:
            return self.state.get_peripheral_desired_actuator_value(
                self.name, self.channel_setpoints_name
            )

    def initialize_peripheral(self) -> None:
        """Initializes peripheral."""
        self.logger.info("Initializing")

        # Clear reported values
        self.clear_reported_values()

        # Initialize health
        self.health = 100.0

        # Initialize driver
        try:
            self.driver = driver.LEDDAC5578Driver(
                name=self.name,
                panel_configs=self.panel_configs,
                panel_properties=self.panel_properties,
                i2c_lock=self.i2c_lock,
                simulate=self.simulate,
                mux_simulator=self.mux_simulator,
            )
            self.health = (
                100.0 * self.driver.num_active_panels / self.driver.num_expected_panels
            )
        except exceptions.DriverError as e:
            self.logger.exception("Manager unable to initialize")
            self.health = 0.0
            self.mode = modes.ERROR

    def setup_peripheral(self) -> None:
        """Sets up peripheral by turning off leds."""
        self.logger.debug("Setting up")
        try:
            self.channel_setpoints = self.driver.turn_off()
            self.health = (
                100.0 * self.driver.num_active_panels / self.driver.num_expected_panels
            )
        except exceptions.DriverError as e:
            self.logger.exception("Unable to setup")
            self.mode = modes.ERROR
            return

        # Update reported variables
        self.update_reported_variables()

    def update_peripheral(self) -> None:
        """Updates peripheral if desired spectrum, intensity, or distance value changes."""

        # Initialize update flag
        update_required = False

        # Check for new desired intensity
        if (
            self.desired_intensity != None
            and self.desired_intensity != self.prev_desired_intensity
        ):
            self.logger.info("Received new desired intensity")
            self.logger.debug(
                "desired_intensity = {} Watts".format(self.desired_intensity)
            )
            self.distance = self.desired_distance
            update_required = True

        # Check for new desired spectrum
        if (
            self.desired_spectrum != None
            and self.desired_spectrum != self.prev_desired_spectrum
        ):
            self.logger.info("Received new desired spectrum")
            self.logger.debug("desired_spectrum = {}".format(self.desired_spectrum))
            update_required = True

        # Check for new illumination distance
        if (
            self.desired_distance != None
            and self.desired_distance != self.prev_desired_distance
        ):
            self.logger.info("Received new desired illumination distance")
            self.logger.debug("desired_distance = {} cm".format(self.desired_distance))
            update_required = True

        # Check if all desired values exist:
        all_desired_values_exist = True
        if (
            self.desired_intensity == None
            or self.desired_spectrum == None
            or self.desired_distance == None
        ):
            all_desired_values_exist = False

        # Check for heartbeat timeout - must send update to device every heartbeat interval
        heartbeat_required = False
        if self.heartbeat_interval != None:
            heartbeat_delta = time.time() - self.prev_heartbeat_time
            if heartbeat_delta > self.heartbeat_interval:
                heartbeat_required = True
                self.prev_heartbeat_time = time.time()

        # Write outputs to hardware every heartbeat interval if update isn't inevitable
        if not update_required and heartbeat_required and all_desired_values_exist:
            self.logger.debug("Sending heatbeat to panels")
            self.driver.set_outputs(self.channel_setpoints)

        # Check for panel re-initialization
        reinit_delta = time.time() - self.prev_reinit_time
        if reinit_delta > self.reinit_interval:
            for panel in self.driver.panels:
                if panel == None:
                    try:
                        message = "Re-initializing panel `{}`".format(panel.name)
                        self.logger.debug(message)
                        panel.initialize()
                    except Exception as e:
                        message = "Unable to re-initialize panel {}".format(panel.name)
                        self.logger.exception(message)
            self.pre_reinit_time = time.time()

        # Check if update is required
        if not update_required:
            return

        # Set spectral power distribution from desired values
        try:
            result = self.driver.set_spd(
                self.desired_distance, self.desired_intensity, self.desired_spectrum
            )
            self.health = (
                100.0 * self.driver.num_active_panels / self.driver.num_expected_panels
            )
        except exceptions.DriverError as e:
            self.logger.exception("Unable to set spd")
            self.mode = modes.ERROR
            self.health = 0
            return

        # Update reported values
        self.logger.debug("self.spectrum = {}".format(self.spectrum))
        self.channel_setpoints = result[0]
        self.spectrum = result[1]
        self.intensity = result[2]

        # Update prev desired values
        self.prev_desired_intensity = self.desired_intensity
        self.prev_desired_spectrum = self.desired_spectrum
        self.prev_desired_distance = self.desired_distance

        # Update latest heartbeat time
        self.prev_heartbeat_time = time.time()

    def clear_reported_values(self) -> None:
        """Clears reported values."""
        self.intensity = None
        self.spectrum = None
        self.distance = None
        self.channel_setpoints = None
        self.prev_desired_intensity = None
        self.prev_desired_spectrum = None
        self.prev_desired_distance = None

    def update_reported_variables(self) -> None:
        """Updates reported variables."""
        self.logger.debug("Updating reported variables")

        # Get previously used distance or default setup distance as average of min
        # and max calibrated distances
        if self.distance == None:

            # Get min/max distance for channels
            intensity_map = self.panel_properties.get(  # type: ignore
                "intensity_map_cm_umol", {}
            )
            distance_list = []
            intensity_list = []
            for distance_, intensity in intensity_map.items():
                distance_list.append(float(distance_))
                intensity_list.append(intensity)
            min_distance = min(distance_list)
            max_distance = max(distance_list)

            # Set distance as average of min and max calibrated distances
            raw_distance = (min_distance + max_distance) / 2
            self.distance = round(raw_distance, 2)

        # Get previously used spectrum or default setup spectrum for reference spd
        if self.spectrum != None:
            reference_spectrum = self.spectrum
        else:
            for channel_key, channel_dict in self.channel_types.items():
                reference_spectrum = channel_dict.get("spectrum_nm_percent", {})
                break

        # Calculate resultant spectrum and intensity
        self.spectrum, self.intensity = light.calculate_resultant_spd(  # type: ignore
            self.panel_properties,
            reference_spectrum,
            self.channel_setpoints,
            self.distance,
        )

    ##### EVENT FUNCTIONS ##############################################################

    def create_peripheral_specific_event(
        self, request: Dict[str, Any]
    ) -> Tuple[str, int]:
        """Processes peripheral specific event."""
        if request["type"] == events.TURN_ON:
            return self.turn_on()
        elif request["type"] == events.TURN_OFF:
            return self.turn_off()
        elif request["type"] == events.SET_CHANNEL:
            return self.set_channel(request)
        elif request["type"] == events.FADE:
            return self.fade()
        else:
            return "Unknown event request type", 400

    def check_peripheral_specific_events(self, request: Dict[str, Any]) -> None:
        """Checks peripheral specific events."""
        if request["type"] == events.TURN_ON:
            self._turn_on()
        elif request["type"] == events.TURN_OFF:
            self._turn_off()
        elif request["type"] == events.SET_CHANNEL:
            self._set_channel(request)
        elif request["type"] == events.FADE:
            self._fade()
        else:
            message = "Invalid event request type in queue: {}".format(request["type"])
            self.logger.error(message)

    def turn_on(self) -> Tuple[str, int]:
        """Pre-processes turn on event request."""
        self.logger.debug("Pre-processing turn on event request")

        # Require mode to be in manual
        if self.mode != modes.MANUAL:
            return "Must be in manual mode", 400

        # Add event request to event queue
        request = {"type": events.TURN_ON}
        self.event_queue.put(request)

        # Successfully turned on
        return "Turning on", 200

    def _turn_on(self) -> None:
        """Processes turn on event request."""
        self.logger.debug("Processing turn on event request")

        # Require mode to be in manual
        if self.mode != modes.MANUAL:
            self.logger.critical("Tried to turn on from {} mode".format(self.mode))

        # Turn on driver and update reported variables
        try:
            self.channel_setpoints = self.driver.turn_on()
            self.update_reported_variables()
        except exceptions.DriverError as e:
            self.mode = modes.ERROR
            message = "Unable to turn on: {}".format(e)
            self.logger.debug(message)
        except:
            self.mode = modes.ERROR
            message = "Unable to turn on, unhandled exception"
            self.logger.exception(message)

    def turn_off(self) -> Tuple[str, int]:
        """Pre-processes turn off event request."""
        self.logger.debug("Pre-processing turn off event request")

        # Require mode to be in manual
        if self.mode != modes.MANUAL:
            return "Must be in manual mode", 400

        # Add event request to event queue
        request = {"type": events.TURN_OFF}
        self.event_queue.put(request)

        # Successfully turned off
        return "Turning off", 200

    def _turn_off(self) -> None:
        """Processes turn off event request."""
        self.logger.debug("Processing turn off event request")

        # Require mode to be in manual
        if self.mode != modes.MANUAL:
            self.logger.critical("Tried to turn off from {} mode".format(self.mode))

        # Turn off driver and update reported variables
        try:
            self.channel_setpoints = self.driver.turn_off()
            self.update_reported_variables()
        except exceptions.DriverError as e:
            self.mode = modes.ERROR
            message = "Unable to turn off: {}".format(e)
            self.logger.debug(message)
        except:
            self.mode = modes.ERROR
            message = "Unable to turn off, unhandled exception"
            self.logger.exception(message)

    def set_channel(self, request: Dict[str, Any]) -> Tuple[str, int]:
        """Pre-processes set channel event request."""
        self.logger.debug("Pre-processing set channel event request")

        # Require mode to be in manual
        if self.mode != modes.MANUAL:
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
        if channel not in self.channel_names:
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
        request = {"type": events.SET_CHANNEL, "channel": channel, "percent": percent}
        self.event_queue.put(request)

        # Return response
        return "Setting {} to {:.0F}%".format(channel, percent), 200

    def _set_channel(self, request: Dict[str, Any]) -> None:
        """Processes set channel event request."""
        self.logger.debug("Processing set channel event")

        # Require mode to be in manual
        if self.mode != modes.MANUAL:
            self.logger.critical("Tried to set channel from {} mode".format(self.mode))

        # Get channel and percent
        channel = request.get("channel")
        percent = float(request.get("percent"))  # type: ignore

        # Set channel and update reported variables
        try:
            self.driver.set_output(channel, percent)
            self.channel_setpoints[channel] = percent
            self.update_reported_variables()
        except exceptions.DriverError as e:
            self.mode = modes.ERROR
            message = "Unable to set channel: {}".format(e)
            self.logger.debug(message)
        except:
            self.mode = modes.ERROR
            message = "Unable to set channel, unhandled exception"
            self.logger.exception(message)

    def fade(self) -> Tuple[str, int]:
        """Pre-processes fade event request."""
        self.logger.debug("Pre-processing fade event request")

        # Require mode to be in manual
        if self.mode != modes.MANUAL:
            return "Must be in manual mode", 400

        # Add event request to event queue
        request = {"type": events.FADE}
        self.event_queue.put(request)

        # Return not implemented yet
        return "Fading", 200

    def _fade(self, channel_name: Optional[str] = None) -> None:
        """Processes fade event request."""
        self.logger.debug("Fading")

        # Require mode to be in manual
        if self.mode != modes.MANUAL:
            self.logger.critical("Tried to fade from {} mode".format(self.mode))

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
                for value in range(0, 110, 10):

                    # Set driver output
                    self.logger.info("Channel {}: {}%".format(channel_name, value))
                    try:
                        self.driver.set_output(channel_name, value)
                    except Exception as e:
                        self.logger.exception("Unable to fade driver")
                        return

                    # Check for events
                    if not self.event_queue.empty():
                        return

                    # Update every 100ms
                    time.sleep(0.1)

                # Fade down
                for value in range(100, -10, -10):

                    # Set driver output
                    self.logger.info("Channel {}: {}%".format(channel_name, value))
                    try:
                        self.driver.set_output(channel_name, value)
                    except Exception as e:
                        self.logger.exception("Unable to fade driver")
                        return

                    # Check for events
                    if not self.event_queue.empty():
                        return

                    # Update every 100ms
                    time.sleep(0.1)
