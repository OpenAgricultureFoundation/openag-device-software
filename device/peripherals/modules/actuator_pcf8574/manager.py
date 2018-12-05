# Import standard python modules
from typing import Optional, Tuple, Dict, Any

# Import peripheral parent class
from device.peripherals.classes.peripheral import manager, modes

# Import manager elements
from device.peripherals.common.pcf8574 import driver
from device.peripherals.modules.actuator_pcf8574 import exceptions, events


class ActuatorPCF8574Manager(manager.PeripheralManager):
    """Manages an actuator controlled by a pcf85764 io expander."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes manager."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize communication variables
        self.port = self.communication["port"]
        self.is_active_high = self.communication["is_active_high"]

        # Initialize variable names
        self.output_name = self.variables["actuator"]["output_variable"]

    @property
    def desired_output(self) -> Optional[float]:
        """Gets desired output value."""
        value = self.state.get_environment_desired_actuator_value(self.output_name)
        if value != None:
            return float(value)
        return None

    @property
    def output(self) -> Optional[float]:
        """Gets reported output value."""
        value = self.state.get_peripheral_reported_actuator_value(
            self.name, self.output_name
        )
        if value != None:
            return float(value)
        return None

    @output.setter
    def output(self, value: float) -> None:
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
            self.driver = driver.PCF8574Driver(
                name=self.name,
                i2c_lock=self.i2c_lock,
                bus=self.bus,
                mux=self.mux,
                channel=self.channel,
                address=self.address,
                simulate=self.simulate,
                mux_simulator=self.mux_simulator,
            )
        except exceptions.DriverError as e:
            self.logger.debug("Unable to initialize: {}".format(e))
            self.health = 0.0
            self.mode = modes.ERROR

    def setup_peripheral(self) -> None:
        """Sets up peripheral."""
        self.logger.debug("No setup required")

    def update_peripheral(self) -> None:
        """Updates sensor by reading temperature and humidity values then 
        reports them to shared state."""

        # Check if desired output is unchanged
        if self.desired_output == None or self.desired_output == self.output:
            return

        # Output has changed, set output and update reported value
        if self.desired_output == 100:
            if self.is_active_high:
                self.driver.set_high(self.port)
            else:
                self.driver.set_low(self.port)
            self.output = self.desired_output
            self.health = 100.0
        elif self.desired_output == 0:
            if self.is_active_high:
                self.driver.set_low(self.port)
            else:
                self.driver.set_high(self.port)
            self.output = self.desired_output
            self.health = 100.0
        else:
            message = "Received invalid desired output value: {}".format(
                self.desired_output
            )
            self.logger.error(message)
            self.health = 0.0
            self.mode = modes.ERROR

    def reset_peripheral(self) -> None:
        """Resets sensor."""
        self.logger.info("Resetting")

        # Clear reported values
        self.clear_reported_values()

    def shutdown_peripheral(self) -> None:
        """Shutsdown peripheral."""
        self.logger.info("Shutting down")
        self.clear_reported_values()

    def clear_reported_values(self) -> None:
        """Clears reported values."""
        self.output = None

    ##### EVENT FUNCTIONS ##############################################################

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
            if self.is_active_high:
                self.driver.set_high(self.port)
            else:
                self.driver.set_low(self.port)
            self.output = 100.0
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
            if self.is_active_high:
                self.driver.set_low(self.port)
            else:
                self.driver.set_high(self.port)
            self.output = 0.0
        except exceptions.DriverError as e:
            self.mode = modes.ERROR
            message = "Unable to turn off: {}".format(e)
            self.logger.debug(message)
        except:
            self.mode = modes.ERROR
            message = "Unable to turn off, unhandled exception"
            self.logger.exception(message)
