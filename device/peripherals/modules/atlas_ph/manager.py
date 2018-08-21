# Import standard python modules
from typing import Optional, Tuple, Dict

# Import device utilities
from device.utilities.modes import Modes

# Import peripheral parent class
from device.peripherals.classes.peripheral_manager import PeripheralManager

# Import module elements
from device.peripherals.modules.atlas_ph.events import AtlasPHEvents
from device.peripherals.modules.atlas_ph.exceptions import DriverError


class AtlasPHManager(PeripheralManager, AtlasPHEvents):
    """ Manages an Atlas Scientific pH sensor. """

    # Initialize compensation temperature parameters
    _temperature_threshold = 0.1  # celcius
    _prev_temperature = 0  # celcius

    def __init__(self, *args, **kwargs):
        """Instantiates sensor. Instantiates parent class, and initializes 
        sensor variable name."""

        # Instantiate parent class
        super().__init__(*args, **kwargs)

        # Initialize variable names
        self.ph_name = self.parameters["variables"]["sensor"]["ph"]
        self.temperature_name = self.parameters["variables"]["compensation"][
            "temperature_celcius"
        ]

    @property
    def ph(self) -> None:
        """ Gets potential hydrogen value. """
        return self.state.get_peripheral_reported_sensor_value(self.name, self.ph_name)

    @ph.setter
    def ph(self, value: float) -> None:
        """Sets potential hydrogen value in shared state. Does not update enironment 
        from calibration mode."""
        self.state.set_peripheral_reported_sensor_value(self.name, self.ph_name, value)
        if self.mode != Modes.CALIBRATE:
            self.state.set_environment_reported_sensor_value(
                self.name, self.ph_name, value
            )

    @property
    def temperature(self) -> None:
        """ Gets compensation temperature value from shared environment state. """
        return self.state.get_environment_reported_sensor_value(self.temperature_name)

    def initialize(self) -> None:
        """Initializes manager."""
        self.logger.info("Initializing")

        # Clear reported values
        self.clear_reported_values()

        # Initialize health
        self.health = 100.0

        # Initialize driver optional parameters
        mux = self.communication.get("mux", None)
        if mux != None:
            mux = int(mux, 16)

        # Initialize driver
        try:
            self.driver = AtlasDriver(
                name=self.name,
                bus=self.communication["bus"],
                address=int(self.communication["address"], 16),
                mux=mux,
                channel=self.communication.get("channel", None),
                simulate=self.simulate,
                mux_simulator=self.mux_simulator,
            )
        except DriverError as e:
            self.logger.exception("Manager unable to initialize")
            self.health = 0.0
            self.mode = Modes.ERROR
            return

    def setup(self) -> None:
        """Sets up sensor."""
        self.logger.debug("Setting up sensor")

        try:
            self.driver.setup()
        except DriverError as e:
            self.logger.error("Unable to setup")
            self.mode = Modes.ERROR
            self.health = 0

    def update(self) -> None:
        """Updates sensor."""

        try:
            # Update compensation temperature if new value
            if self.new_compensation_temperature():
                self.driver.set_compensation_temperature(float(self.temperature))

            # Read pH and update health
            self.ph = self.driver.read_ph()
            self.health = 100.0

        except DriverError as e:
            self.logger.error("Unable to update")
            self.mode = Modes.ERROR
            self.health = 0
            return

    def reset(self) -> None:
        """Resets sensor."""
        self.logger.info("Resetting")
        self.clear_reported_values()

    def shutdown(self) -> None:
        """Shuts down sensor."""
        self.logger.info("Shutting down sensor")
        self.clear_reported_values()

    def new_compensation_temperature(self) -> bool:
        """Check if there is a new compensation temperature value."""

        # Check if calibrating
        if self.mode == Modes.CALIBRATE:
            return False

        # Check if compensation temperature exists
        if self.temperature == None:
            return False

        # Check if temperature value sufficiently different
        if abs(self.temperature - self._prev_temperature) < self._temperature_threshold:
            return False

        # New compensation temperature exists
        return True

    def clear_reported_values(self) -> None:
        """Clears reported values."""
        self.ph = None
