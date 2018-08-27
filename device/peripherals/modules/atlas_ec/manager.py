# Import standard python modules
from typing import Optional, Tuple, Dict

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.health import Health
from device.utilities.error import Error

# Import peripheral parent class
from device.peripherals.classes.peripheral_manager import PeripheralManager

# Import led array and events
from device.peripherals.modules.atlas_ec.sensor import AtlasECSensor
from device.peripherals.modules.atlas_ec.events import AtlasECEvents


class AtlasECManager(PeripheralManager, AtlasECEvents):
    """ Manages an Atlas Scientific electrical conductivity sensor. """

    # Initialize compensation temperature parameters
    temperature_threshold = 0.1  # celcius
    prev_temperature = 0  # celcius

    def __init__(self, *args, **kwargs):
        """Initializes manager."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize variable names
        self.ec_name = self.parameters["variables"]["sensor"]["ec_ms_cm"]
        self.temperature_name = self.parameters["variables"]["compensation"][
            "temperature_celcius"
        ]

        # Initialize sensor
        self.sensor = AtlasECSensor(
            name=self.name,
            bus=self.parameters["communication"]["bus"],
            mux=int(self.parameters["communication"]["mux"], 16),
            channel=self.parameters["communication"]["channel"],
            address=int(self.parameters["communication"]["address"], 16),
            simulate=self.simulate,
        )

    @property
    def ec(self) -> None:
        """ Gets electrical conductivity value. """
        return self.state.get_peripheral_reported_sensor_value(self.name, self.ec_name)

    @ec.setter
    def ec(self, value: float) -> None:
        """ Sets electrical conductivity value in shared state. Does not update enironment from calibration mode. """
        self.state.set_peripheral_reported_sensor_value(self.name, self.ec_name, value)
        if self.mode != Modes.CALIBRATE:
            self.state.set_environment_reported_sensor_value(
                self.name, self.ec_name, value
            )

    @property
    def temperature(self) -> None:
        """ Gets compensation temperature value from shared environment state. """
        return self.state.get_environment_reported_sensor_value(self.temperature_name)

    def initialize(self) -> None:
        """ Initializes manager."""
        self.logger.debug("Initializing")

        # Clear reported values
        self.clear_reported_values()

        # Initialize health
        self.health = self.sensor.health.percent

        # Initialize sensor
        error = self.sensor.probe()

        # Check for errors
        if error.exists():
            error.report("Manager unable to initialize")
            self.logger.error(error.summary())
            self.mode = Modes.ERROR
            return

        # Successful initialization!
        self.logger.debug("Initialized successfully")

    def setup(self) -> None:
        """ Sets up manager. Programs device operation parameters into 
            sensor driver circuit. """
        self.logger.debug("Setting up sensor")

        # Setup sensor
        error = self.sensor.setup()

        # Check for errors:
        if error.exists():
            error.report("Manager setup failed")
            self.logger.error(error.summary())
            self.mode = Modes.ERROR
            return

        # Successfully setup!
        self.logger.debug("Successfully setup!")

    def update(self) -> None:
        """ Updates sensor when in normal mode. """

        # Update compensation temperature if new value
        if self.new_compensation_temperature():

            # Set compensation temperature
            error = self.sensor.set_compensation_temperature(self.temperature)
            self.prev_temperature = self.temperature

            # Check for errors
            if error.exists():
                error.report("Manager unable to update")
                self.logger.error(error.summary())
                self.mode = Modes.ERROR
                self.health = self.sensor.health.percent
                return

        # Read electrical conductivity
        ec, error = self.sensor.read_ec()

        # Check for errors:
        if error.exists():
            error.report("Manager unable to update")
            self.logger.error(error.summary())
            self.mode = Modes.ERROR
            self.health = self.sensor.health.percent
            return

        # Update reported values
        self.ec = ec
        self.health = self.sensor.health.percent

    def reset(self) -> None:
        """ Resets sensor. """
        self.logger.info("Resetting")

        # Clear reported values
        self.clear_reported_values()

        # Reset sensor
        self.sensor.reset()

        # Sucessfully reset!
        self.logger.debug("Successfully reset!")

    def shutdown(self) -> None:
        """ Shuts down sensor. """
        self.logger.info("Shutting down sensor")

        # Clear reported values
        self.clear_reported_values()

    def new_compensation_temperature(self) -> bool:
        """ Check if there is a new compensation temperature value. """

        # Check if calibrating
        if self.mode == Modes.CALIBRATE:
            return False

        # Check if compensation temperature exists
        if self.temperature == None:
            return False

        # Check if temperature value sufficiently different
        if abs(self.temperature - self.prev_temperature) < self.temperature_threshold:
            return False

        # New compensation temperature exists!
        return True

    def clear_reported_values(self) -> None:
        """ Clears reported values. """
        self.ec = None
