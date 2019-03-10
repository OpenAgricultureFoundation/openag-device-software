# Import standard python modules
import time

# Import python types
from typing import Optional, Tuple, Dict, Any

# Import peripheral parent class
from device.peripherals.classes.peripheral import manager, modes

# Import manager elements
from device.peripherals.modules.actuator_grove_rgb_lcd import exceptions, events, driver


#debugrob: fix here down, fix turn_on/off bool stuff

class ActuatorGroveRGBLCDManager(manager.PeripheralManager):
    """Manages an actuator controlled by a Grove RGB LCD."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes manager."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize communication variables
        self.bus = self.communication.get("bus")
        self.mux = self.communication.get("mux")
        self.rgb_address = self.communication.get("rgb_address")
        self.lcd_address = self.communication.get("lcd_address")

        if self.bus == "none":
            self.bus = None
        if self.mux == "none":
            self.mux = None
        if self.rgb_address is None:
            self.logger.critical("Missing RGB I2C address")
            return
        if self.lcd_address is None:
            self.logger.critical("Missing LCD I2C address")
            return

        # Convert i2c config params from hex to int if they exist
        self.rgb_address = int(self.rgb_address, 16)
        self.lcd_address = int(self.lcd_address, 16)
        if self.bus is not None:
            self.bus = int(self.bus)
        if self.mux is not None:
            self.mux = int(self.mux, 16)

        self.logger.info("rgb_address=0x{:02X}, lcd_address=0x{:02X}"
                .format(self.rgb_address, self.lcd_address))

#debugrob: validate with setup json, need to figure out how this reads temp and humidity sensor values in the state.  Look at controller code?
        # Initialize variable names
        self.output_name = "message"
        act = self.variables.get("actuator")
        if act is not None:
            self.output_name = act.get("output_variable")

        # Set default sampling interval and heartbeat
        self.default_sampling_interval = 5 # seconds
        self.heartbeat = 60  # seconds
        self.prev_update = 0  # timestamp

    @property
    def desired_output(self) -> Optional[bool]:
        """Gets desired output value."""
        value = self.state.get_environment_desired_actuator_value(self.output_name)
        if value != None:
            return bool(value)
        return None

    @property
    def output(self) -> Optional[bool]:
        """Gets reported output value."""
        value = self.state.get_peripheral_reported_actuator_value(
            self.name, self.output_name
        )
        if value != None:
            return bool(value)
        return None

    @output.setter
    def output(self, value: bool) -> None:
        """Sets reported output value in shared state."""
        self.state.set_peripheral_reported_actuator_value(
            self.name, self.output_name, value
        )
        self.state.set_environment_reported_actuator_value(self.output_name, value)

    def initialize_peripheral(self) -> None:
        """Initializes manager."""
        self.logger.info("Initializing")

        # Clear reported values
        self.clear_reported_values()

        # Initialize health
        self.health = 100.0

        # Initialize driver
        try:
            self.driver = driver.GroveRGBLCDDriver(
                name=self.name,
                i2c_lock=self.i2c_lock,
                bus=self.bus,
                rgb_address=self.rgb_address,
                lcd_address=self.lcd_address,
                mux=self.mux,
                channel=self.channel,
                simulate=self.simulate,
                mux_simulator=self.mux_simulator,
            )
        except exceptions.DriverError as e:
            self.logger.exception("Unable to initialize: {}".format(e))
            self.health = 0.0
            self.mode = modes.ERROR

    def setup_peripheral(self) -> None:
        """Sets up peripheral."""
        self.logger.debug("Setting up peripheral")
        try:
            self.set_off()
        except exceptions.DriverError as e:
            self.logger.exception("Unable to setup: {}".format(e))
            self.mode = modes.ERROR
            self.health = 0.0

    def update_peripheral(self) -> None:
        """Updates peripheral by setting output to desired state."""
        try:
            # Check if desired output is not set
            if self.desired_output == None and self.output != 0.0:
                self.set_off()

            # Check if output is set to desired value
            elif self.desired_output != None and self.output != self.desired_output:
                self.set_output(self.desired_output)

            # Check for heartbeat
            if time.time() - self.prev_update > self.heartbeat:
                self.logger.debug("Sending heartbeat")
                self.set_output(self.output)

        except exceptions.DriverError as e:
            self.logger.exception("Unable to update peripheral: {}".format(e))
            self.mode = modes.ERROR
            self.health = 0.0

    def reset_peripheral(self) -> None:
        """Resets sensor."""
        self.logger.info("Resetting")
        self.clear_reported_values()

    def shutdown_peripheral(self) -> None:
        """Shutsdown peripheral."""
        self.logger.info("Shutting down")
        try:
            self.set_off()
        except exceptions.DriverError as e:
            message = "Unable to turn off actuator before shutting down: {}".format(
                type(e)
            )
            self.logger.warning(message)
        self.clear_reported_values()

    def clear_reported_values(self) -> None:
        """Clears reported values."""
        self.output = None

    ##### HELPER FUNCTIONS ####################################################

    def set_output(self, value: bool):
        """Sets output."""
        if value:
            self.set_on()
        else:
            self.set_off()

    def set_on(self):
        """Sets driver on."""
        self.logger.debug("Setting on")
#debugrob: 
        self.driver.blah()
        self.output = True
        self.health = 100.0
        self.prev_update = time.time()

    def set_off(self):
        """Sets driver off."""
        self.logger.debug("Setting off")
#debugrob: 
        self.output = False
        self.health = 100.0
        self.prev_update = time.time()

    ##### EVENT FUNCTIONS #####################################################

    def create_peripheral_specific_event(
        self, request: Dict[str, Any]
    ) -> Tuple[str, int]:
        """Processes peripheral specific event."""
        if request["type"] == events.TURN_ON:
            return self.turn_on()
        elif request["type"] == events.TURN_OFF:
            return self.turn_off()
        else:
            return "Unknown event request type", 400

    def check_peripheral_specific_events(self, request: Dict[str, Any]) -> None:
        """Checks peripheral specific events."""
        if request["type"] == events.TURN_ON:
            self._turn_on()
        elif request["type"] == events.TURN_OFF:
            self._turn_off()
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
            self.set_on()
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
            self.set_off()
        except exceptions.DriverError as e:
            self.mode = modes.ERROR
            message = "Unable to turn off: {}".format(e)
            self.logger.debug(message)
        except:
            self.mode = modes.ERROR
            message = "Unable to turn off, unhandled exception"
            self.logger.exception(message)
