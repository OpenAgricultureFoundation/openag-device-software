# Import standard python modules
from typing import Optional, Tuple, Dict, Any

# Import manager elements
from device.peripherals.classes.peripheral import manager, modes
from device.peripherals.classes.atlas import exceptions
from device.peripherals.modules.atlas_ph import driver, events


class AtlasPHManager(manager.PeripheralManager):
    """Manages an Atlas Scientific pH sensor."""

    # Initialize compensation temperature parameters
    temperature_threshold = 0.1  # celsius
    prev_temperature = 0.0  # celsius

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes manager."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize variable names
        self.ph_name = self.variables["sensor"]["ph"]
        self.temperature_name = self.variables["compensation"]["temperature_celsius"]

    @property
    def ph(self) -> Optional[float]:
        """Gets pH value."""
        value = self.state.get_peripheral_reported_sensor_value(self.name, self.ph_name)
        if value != None:
            return float(value)
        return None

    @ph.setter
    def ph(self, value: float) -> None:
        """Sets pH value in shared state. Does not update enironment 
        from calibration mode."""
        self.state.set_peripheral_reported_sensor_value(self.name, self.ph_name, value)
        if self.mode != modes.CALIBRATE:
            self.state.set_environment_reported_sensor_value(
                self.name, self.ph_name, value
            )

    @property
    def temperature(self) -> Optional[float]:
        """Gets compensation temperature value from shared environment state."""
        value = self.state.get_environment_reported_sensor_value(self.temperature_name)
        if value != None:
            return float(value)
        return None

    def initialize_peripheral(self) -> None:
        """Initializes peripheral."""
        self.logger.info("Initializing")

        # Clear reported values
        self.clear_reported_values()

        # Initialize health
        self.health = 100.0

        # Initialize driver
        try:
            self.driver = driver.AtlasPHDriver(
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
            # Update compensation temperature if new value
            if self.new_compensation_temperature():
                self.driver.set_compensation_temperature(self.temperature)

            # Read pH and update health
            self.ph = self.driver.read_ph()
            self.health = 100.0

        except exceptions.DriverError as e:
            self.logger.error("Unable to update")
            self.mode = modes.ERROR
            self.health = 0

    def clear_reported_values(self) -> None:
        """Clears reported values."""
        self.ph = None

    def new_compensation_temperature(self) -> bool:
        """Checks if there is a new compensation temperature value."""

        # Check if calibrating
        if self.mode == modes.CALIBRATE:
            return False

        # Check if compensation temperature exists
        if self.temperature == None:
            return False

        # Check if temperature value sufficiently different
        delta = abs(self.temperature - self.prev_temperature)  # type: ignore
        if delta < self.temperature_threshold:
            return False

        # New compensation temperature exists
        return True

    ##### EVENT FUNCTIONS ##############################################################

    def create_peripheral_specific_event(
        self, request: Dict[str, Any]
    ) -> Tuple[str, int]:
        """Processes peripheral specific event."""
        if request["type"] == events.CALIBRATE_LOW:
            return self.calibrate_low(request)
        elif request["type"] == events.CALIBRATE_MID:
            return self.calibrate_mid(request)
        elif request["type"] == events.CALIBRATE_HIGH:
            return self.calibrate_high(request)
        elif request["type"] == events.CLEAR_CALIBRATION:
            return self.clear_calibration()
        else:
            return "Unknown event request type", 400

    def check_peripheral_specific_events(self, request: Dict[str, Any]) -> None:
        """Checks peripheral specific events."""
        if request["type"] == events.CALIBRATE_LOW:
            self._calibrate_low(request)
        elif request["type"] == events.CALIBRATE_MID:
            self._calibrate_mid(request)
        elif request["type"] == events.CALIBRATE_HIGH:
            self._calibrate_high(request)
        elif request["type"] == events.CLEAR_CALIBRATION:
            self._clear_calibration()
        else:
            message = "Invalid event request type in queue: {}".format(request["type"])
            self.logger.error(message)

    def calibrate_low(self, request: Dict[str, Any]) -> Tuple[str, int]:
        """Pre-processes calibrate low event request."""
        self.logger.info("Pre-processing calibrate low event request")

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

        # Verify value within valid range
        if value not in range(4, 10):
            message = "Invalid request value, not in range 4-10"
            self.logger.debug(message)
            return message, 400

        # Require mode to be in CALIBRATE
        if self.mode != modes.CALIBRATE:
            message = "Must be in calibration mode to take single point calibration"
            self.logger.debug(message)
            return message, 400

        # Add event request to event queue
        request = {"type": events.CALIBRATE_LOW, "value": value}
        self.event_queue.put(request)

        # Return response
        return "Taking low point calibration reading", 200

    def _calibrate_low(self, request: Dict[str, Any]) -> None:
        """Processes calibrate low event request."""
        self.logger.info("Processing calibrate low event request")

        # Require mode to be in CALIBRATE
        if self.mode != modes.CALIBRATE:
            message = "Tried to calibrate low from {} mode".format(self.mode)
            self.logger.critical(message)
            return

        # Send command
        try:
            value = float(request["value"])
            self.driver.calibrate_low(value)
        except exceptions.DriverError:
            self.logger.exception("Unable to calibrate low")

    def calibrate_mid(self, request: Dict[str, Any]) -> Tuple[str, int]:
        """Pre-processes calibrate mid event request."""
        self.logger.info("Pre-processing calibrate mid event request")

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

        # Verify value within valid range
        if value not in range(4, 10):
            message = "Invalid request value, not in range 4-10"
            self.logger.debug(message)
            return message, 400

        # Require mode to be in CALIBRATE
        if self.mode != modes.CALIBRATE:
            message = "Must be in calibration mode to take single point calibration"
            self.logger.debug(message)
            return message, 400

        # Add event request to event queue
        request = {"type": events.CALIBRATE_MID, "value": value}
        self.event_queue.put(request)

        # Return reponse
        return "Taking mid point calibration reading", 200

    def _calibrate_mid(self, request: Dict[str, Any]) -> None:
        """Processes calibrate mid event request."""
        self.logger.info("Processing calibrate mid event request")

        # Require mode to be in CALIBRATE
        if self.mode != modes.CALIBRATE:
            message = "Tried to calibrate mid from {} mode".format(self.mode)
            self.logger.critical(message)
            return

        # Send command
        try:
            value = float(request["value"])
            self.driver.calibrate_mid(value)
        except exceptions.DriverError:
            self.logger.exception("Unable to calibrate mid")

    def calibrate_high(self, request: Dict[str, Any]) -> Tuple[str, int]:
        """Pre-processes calibrate high event request."""
        self.logger.info("Pre-processing calibrate high event request")

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

        # Verify value within valid range
        if value not in range(10, 14):
            message = "Invalid request value, not in range 10-14"
            self.logger.debug(message)
            return message, 400

        # Require mode to be in CALIBRATE
        if self.mode != modes.CALIBRATE:
            message = "Must be in calibration mode to take single point calibration"
            self.logger.debug(message)
            return message, 400

        # Add event request to event queue
        request = {"type": events.CALIBRATE_HIGH, "value": value}
        self.event_queue.put(request)

        # Return response
        return "Taking high point calibration reading", 200

    def _calibrate_high(self, request: Dict[str, Any]) -> None:
        """Processes calibrate high event request."""
        self.logger.debug("Processing calibrate high event request")

        # Require mode to be in CALIBRATE
        if self.mode != modes.CALIBRATE:
            message = "Tried to calibrate high from {} mode".format(self.mode)
            self.logger.critical(message)
            return

        # Send command
        try:
            value = float(request["value"])
            self.driver.calibrate_high(value)
        except exceptions.DriverError:
            self.logger.exception("Unable to calibrate high")

    def clear_calibration(self) -> Tuple[str, int]:
        """ Pre-processes clear calibration event request."""
        self.logger.debug("Pre-processing clear calibration event request")

        # Require mode to be in CALIBRATE
        if self.mode != modes.CALIBRATE:
            message = "Must be in calibration mode to clear calibration"
            self.logger.debug(message)
            return message, 400

        # Add event request to event queue
        request = {"type": events.CLEAR_CALIBRATION}
        self.event_queue.put(request)

        # Return response
        return "Clearing calibration readings", 200

    def _clear_calibration(self) -> None:
        """ Processes clear calibration event request."""
        self.logger.info("Processing clear calibration event request")

        # Require mode to be in CALIBRATE
        if self.mode != modes.CALIBRATE:
            message = "Tried to clear calibration from {} mode".format(self.mode)
            self.logger.debug(message)
            return

        # Send command
        try:
            self.driver.clear_calibrations()
        except exceptions.DriverError:
            self.logger.exception("Unable to clear calibrations")
