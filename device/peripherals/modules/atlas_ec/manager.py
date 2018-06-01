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
from device.peripherals.modules.atlas_ec.events import EventMixin


class AtlasEC(PeripheralManager, EventMixin):
    """ Manages an Atlas Scientific electrical conductivity sensor. """

    # Initialize temperature compensation parameters
    _temperature_threshold_celcius = 0.1
    _prev_temperature_celcius = 0


    def __init__(self, *args, **kwargs):
        """ Instantiates light array. Instantiates parent class, and initializes 
            sensor variable name. """

        # Instantiate parent class
        super().__init__(*args, **kwargs)

        # Initialize variable names
        self.electrical_conductivity_name = self.parameters["variables"]["sensor"]["electrical_conductivity_ms_cm"]
        self.temperature_name = self.parameters["variables"]["compensation"]["temperature_celcius"]

        # Initialize driver
        self.sensor = AtlasECSensor(
            name = self.name, 
            bus = self.parameters["communication"]["bus"], 
            mux = self.parameters["communication"]["mux"],
            channel = self.parameters["communication"]["channel"],
            address = self.parameters["communication"]["address"], 
            simulate = self.simulate,
        )


    @property
    def electrical_conductivity(self) -> None:
        """ Gets electrical conductivity value. """
        return self.state.get_peripheral_reported_sensor_value(self.name, self.electrical_conductivity_name)


    @electrical_conductivity.setter
    def electrical_conductivity(self, value: float) -> None:
        """ Sets electrical conductivity value in shared state. Does not update enironment from calibration mode. """
        self.state.set_peripheral_reported_sensor_value(self.name, self.electrical_conductivity_name, value)
        if self.mode != Modes.CALIBRATE:
            self.state.set_environment_reported_sensor_value(self.name, self.electrical_conductivity_name, value)


    @property
    def temperature(self) -> None:
        """ Gets compensation temperature value from shared environment state. """
        return self.state.get_environment_reported_sensor_value(self.temperature_name)


    def initialize(self) -> None:
        """ Initializes manager."""
        self.logger.debug("Initializing")

        # Clear reported values
        self.clear_reported_values()

        # Initialize sensor
        error = self.sensor.probe()

        # Check for errors
        if error.exists():
            error.report("Manager unable to initialize")
            self.logger.warning(error.trace)
            self.mode = Modes.ERROR
            return

        # Successful initialization!
        self.logger.debug("Initialized successfully")


    def setup(self):
        """ Sets up manager. Programs device operation parameters into 
            sensor driver circuit. """
        self.logger.debug("Setting up sensor")

        # Setup sensor
        error = self.sensor.setup()

        # Check for errors:
        if error.exists():
            error.report("Manager unable to be setup")
            self.logger.warning(error.trace)
            self.mode = Modes.ERROR
            return

        # Successfully setup!
        self.logger.debug("Successfully setup!")   


    def update(self):
        """ Updates sensor when in normal mode. """
        self.update_compensation_temperature()
        self.update_electrical_conductivity()
        self.update_health()
                

    def reset(self):
        """ Resets sensor. """
        self.logger.info("Resetting")

        # Clear reported values
        self.clear_reported_values()

        # Reset sensor
        self.sensor.reset()

        # Sucessfully reset!
        self.logger.debug("Successfully reset!")


    def shutdown(self):
        """ Shuts down sensor. """
        self.logger.info("Shutting down sensor")

        # Clear reported values
        self.clear_reported_values()

        # Shutdown sensor
        self.sensor.shutdown()

        # Send enable sleep command to sensor hardware
        try:
            self.enable_sleep_mode()
            self.logger.debug("Successfully shutdown sensor")
        except:
            self.logger.exception("Sensor shutdown failed")
            self.mode = Modes.ERROR



    def update_electrical_conductivity(self):
        """ Updates sensor electrical conductivity. """
        self.logger.debug("Getting electrical conductivity")
        try:
            self.electrical_conductivity_ms_cm = self.read_electrical_conductivity_ms_cm()
        except:
            self.logger.exception("Unable to update electrical conductivity, bad reading")
            self._missed_readings += 1


    def update_compensation_temperature(self):
        """ Updates sensor compensation temperature on if temperature value exists
            in shared state. Only sets on new values greater than threshold. """

        # Don't update compensation temperature from calibrate mode
        if self.mode == Modes.CALIBRATE:
            self.logger.debug("No need to update compensation temperature when in CALIBRATE mode")
            return

        # Check if there is a temperature value in shared state to compensate with
        temperature_celcius = self.temperature_celcius
        if temperature_celcius == None:
            self.logger.debug("No temperature value in shared state to compensate with")
            return

        # Check if temperature value on sensor requires an update
        temperature_delta_celcius = abs(self._prev_temperature_celcius - temperature_celcius)
        if temperature_delta_celcius < self._temperature_threshold_celcius:
            self.logger.debug("Device temperature compensation does not require update, value within threshold")
            return

        # Update sensor temperature compensation value
        self._prev_temperature_celcius = temperature_celcius
        try:
            self.set_compensation_temperature_celcius(temperature_celcius)
        except:
            self.logger.warning("Unable to set sensor compensation temperature")


    def clear_reported_values(self):
        """ Clears reported values. """
        self.electrical_conductivity = None