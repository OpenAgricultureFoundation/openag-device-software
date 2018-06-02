# Import standard python modules
from typing import Optional, Tuple, Dict

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.health import Health
from device.utilities.error import Error

# Import peripheral parent class
from device.peripherals.classes.peripheral_manager import PeripheralManager

# Import led array and events
from device.peripherals.modules.atlas_do.sensor import AtlasDOSensor
from device.peripherals.modules.atlas_do.events import AtlasDOEvents


class AtlasDO(PeripheralManager, AtlasDOEvents):
    """ Manages an Atlas Scientific dissolved oxygen sensor. """

    # Initialize variable parameters
    _temperature_threshold = 0.1 # celcius
    _prev_temperature = 0
    _pressure_threshold = 0.1 # kPa
    _prev_pressure = 0
    _electrical_conductivity_threshold = 0.1 # mS/cm
    _prev_electrical_conductivity = 0
    

    def __init__(self, *args, **kwargs):
        """ Instantiates manager. Instantiates parent class, and initializes 
            sensor variable name. """

        # Instantiate parent class
        super().__init__(*args, **kwargs)

        # Initialize variable names
        self.dissolved_oxygen_name = self.parameters["variables"]["sensor"]["dissolved_oxygen_mg_l"]
        self.temperature_name = self.parameters["variables"]["compensation"]["temperature_celcius"]
        self.pressure_name = self.parameters["variables"]["compensation"]["pressure_kpa"]
        self.electrical_conductivity_name = self.parameters["variables"]["compensation"]["electrical_conductivity_ms_cm"]

        # Initialize sensor
        self.sensor = AtlasDOSensor(
            name = self.name, 
            bus = self.parameters["communication"]["bus"], 
            mux = int(self.parameters["communication"]["mux"], 16),
            channel = self.parameters["communication"]["channel"],
            address = int(self.parameters["communication"]["address"], 16), 
            simulate = self.simulate,
        )


    @property
    def dissolved_oxygen(self) -> None:
        """ Gets dissolved oxygen value. """
        return self.state.get_peripheral_reported_sensor_value(self.name, self.dissolved_oxygen_name)


    @dissolved_oxygen.setter
    def dissolved_oxygen(self, value: float) -> None:
        """ Sets dissolved oxygen value in shared state. Does not update enironment from calibration mode. """
        self.state.set_peripheral_reported_sensor_value(self.name, self.dissolved_oxygen_name, value)
        if self.mode != Modes.CALIBRATE:
            self.state.set_environment_reported_sensor_value(self.name, self.dissolved_oxygen_name, value)


    @property
    def temperature(self) -> None:
        """ Gets compensation temperature value from shared environment state. """
        return self.state.get_environment_reported_sensor_value(self.temperature_name)


    @property
    def pressure(self) -> None:
        """ Gets compensation pressure value from shared environment state. """
        return self.state.get_environment_reported_sensor_value(self.pressure_name)


    @property
    def electrical_conductivity(self) -> None:
        """ Gets compensation electrical conductivity value from shared environment state. """
        return self.state.get_environment_reported_sensor_value(self.electrical_conductivity_name)


    def initialize(self) -> None:
        """ Initializes manager."""
        self.logger.debug("Initializing")

        # Clear reported values
        self.clear_reported_values()

        # Initialize sensor
        error = self.sensor.probe()

        # Initialize health
        self.health = self.sensor.health.percent

        # Check for errors
        if error.exists():
            error.report("Manager unable to initialize")
            self.logger.warning(error.trace)
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
            self.logger.warning(error.trace)
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

            # Check for errors
            if error.exists():
                error.report("Manager unable to update")
                self.logger.warning(error.trace)
                self.mode = Modes.ERROR
                self.health = self.sensor.health.percent
                return

        # Update compensation pressure if new value
        if self.new_compensation_pressure():

            # Set compensation temperature
            error = self.sensor.set_compensation_pressure(self.pressure)

            # Check for errors
            if error.exists():
                error.report("Manager unable to update")
                self.logger.warning(error.trace)
                self.mode = Modes.ERROR
                self.health = self.sensor.health.percent
                return

        # Update compensation electrical conductivity if new value
        if self.new_compensation_electrical_conductivity():

            # Set compensation temperature
            error = self.sensor.set_compensation_electrical_conductivity(self.electrical_conductivity)

            # Check for errors
            if error.exists():
                error.report("Manager unable to update")
                self.logger.warning(error.trace)
                self.mode = Modes.ERROR
                self.health = self.sensor.health.percent
                return

        # Read dissolved oxygen
        do, error = self.sensor.read_dissolved_oxygen()

        # Check for errors:
        if error.exists():
            error.report("Manager unable to update")
            self.logger.warning(error.trace)
            self.mode = Modes.ERROR
            self.health = self.sensor.health.percent
            return

        # Update ec and health
        self.health = self.sensor.health.percent
        self.dissolved_oxygen = do


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
        if abs(self.temperature - self._prev_temperature) < self._temperature_threshold:
            return False

        # New compensation temperature exists!
        return True


    def new_compensation_pressure(self) -> bool:
        """ Check if there is a new compensation pressure value. """

        # Check if calibrating
        if self.mode == Modes.CALIBRATE:
            return False

        # Check if compensation temperature exists
        if self.pressure == None:
            return False

        # Check if pressure value sufficiently different
        if abs(self.pressure - self._prev_pressure) < self._pressure_threshold:
            return False

        # New compensation pressure exists!
        return True


    def new_compensation_electrical_conductivity(self) -> bool:
        """ Check if there is a new compensation electrical conductivity value. """

        # Check if calibrating
        if self.mode == Modes.CALIBRATE:
            return False

        # Check if compensation temperature exists
        if self.electrical_conductivity == None:
            return False

        # Check if electrical conductivity value sufficiently different
        if abs(self.electrical_conductivity - self._prev_electrical_conductivity) < self._electrical_conductivity_threshold:
            return False

        # New compensation electrical conductivity exists!
        return True


    def clear_reported_values(self) -> None:
        """ Clears reported values. """
        self.dissolved_oxygen = None
