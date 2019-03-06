# Import standard python modules
from typing import Optional, Tuple, Dict, Any

# Import manager elements
from device.peripherals.classes.peripheral import manager, modes
from device.peripherals.classes.atlas import exceptions
from device.peripherals.modules.atlas_temp import driver, events


class AtlasTempManager(manager.PeripheralManager):
    """ Manages an Atlas Scientific temperature driver. """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes manager."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize variable names
        self.temperature_name = self.variables["sensor"]["temperature"]

    @property
    def temperature(self) -> Optional[float]:
        """Gets temperature value."""
        value = self.state.get_peripheral_reported_sensor_value(
            self.name, self.temperature_name
        )
        if value != None:
            return float(value)
        return None

    @temperature.setter
    def temperature(self, value: float) -> None:
        """Sets temperature value in shared state. Does not update enironment from
        calibration mode."""
        self.state.set_peripheral_reported_sensor_value(
            self.name, self.temperature_name, value
        )
        if self.mode != modes.CALIBRATE:
            self.state.set_environment_reported_sensor_value(
                self.name, self.temperature_name, value
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
            self.driver = driver.AtlasTempDriver(
                name=self.name,
                i2c_lock=self.i2c_lock,
                bus=self.bus,
                address=self.address,
                mux=self.mux,
                channel=self.channel,
                simulate=self.simulate,
                mux_simulator=self.mux_simulator,
            )
        except exceptions.DriverError as e:
            self.logger.exception("Unable to initialize")
            self.health = 0.0
            self.mode = modes.ERROR

    def setup_peripheral(self) -> None:
        """Sets up peripheral."""
        self.logger.info("Setting up")

        try:
            self.driver.setup()
        except exceptions.DriverError as e:
            self.logger.exception("Unable to setup")
            self.mode = modes.ERROR
            self.health = 0

    def update_peripheral(self) -> None:
        """Updates peripheral."""
        self.logger.info("Updating")

        try:
            self.temperature = self.driver.read_temperature()
            self.health = 100.0
        except exceptions.DriverError as e:
            self.logger.error("Unable to update")
            self.mode = modes.ERROR
            self.health = 0
            return

    def clear_reported_values(self) -> None:
        """Clears reported values."""
        self.temperature = None

    ##### EVENT FUNCTIONS ##############################################################

    def create_peripheral_specific_event(
        self, request: Dict[str, Any]
    ) -> Tuple[str, int]:
        """Processes peripheral specific event."""
        if request["type"] == events.CALIBRATE:
            return self.calibrate(request)
        else:
            return "Unknown event request type", 400

    def check_peripheral_specific_events(self, request: Dict[str, Any]) -> None:
        """Checks peripheral specific events."""
        type_ = request.get("type")
        if request["type"] == events.CALIBRATE:
            self._calibrate(request)
        else:
            self.logger.error("Invalid event request type in queue: {}".format(type_))

    def calibrate(self, request: Dict[str, Any]) -> Tuple[str, int]:
        """Pre-processes calibrate event request."""
        self.logger.debug("Pre-processing calibrate event request")

        # Verify value in request
        try:
            value = float(request["value"])
        except KeyError as e:
            message = "Invalid request parameters: {}".format(e)
            self.logger.debug(message)
            return message, 400
        except ValueError as e:
            message = "Invalid request value: `{}`".format(request["value"])
            self.logger.debug(message)
            return message, 400

        # Require mode to be in calibrate
        if self.mode != modes.CALIBRATE:
            message = "Must be in calibration mode to take calibration"
            self.logger.debug(message)
            return message, 400

        # Add event request to event queue
        request = {"type": events.CALIBRATE, "value": value}
        self.event_queue.put(request)

        # Return response
        return "Taking dry calibration reading", 200

    def _calibrate(self, request: Dict[str, Any]) -> None:
        """Processes calibrate event request."""
        self.logger.debug("Processing calibrate event request")

        # Require mode to be in calibrate
        if self.mode != modes.CALIBRATE:
            message = "Tried to calibrate from {} mode.".format(self.mode)
            self.logger.critical(message)
            return

        # Send command
        try:
            self.driver.calibrate()
        except exceptions.DriverError:
            self.logger.exception("Unable to calibrate")
