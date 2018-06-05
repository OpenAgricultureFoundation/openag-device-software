# Import standard python modules
from typing import Optional, Tuple, Dict

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.health import Health
from device.utilities.error import Error

# Import peripheral parent class
from device.peripherals.classes.peripheral_manager import PeripheralManager

# Import led array and events
from device.peripherals.modules.sht25.sensor import SHT25Sensor
from device.peripherals.modules.sht25.events import SHT25Events


class SHT25(PeripheralManager, SHT25Events):
    """ Manages an sht25 temperature and humidity sensor. """

    def __init__(self, *args, **kwargs):
        """ Instantiates manager Instantiates parent class, and initializes 
            sensor variable name. """

        # Instantiate parent class
        super().__init__(*args, **kwargs)

        # Initialize variable names
        self.temperature_name = self.parameters["variables"]["sensor"]["temperature_celcius"]
        self.humidity_name = self.parameters["variables"]["sensor"]["humidity_percent"]

        # Initialize sensor
        self.sensor = SHT25Sensor(
            name = self.name, 
            bus = self.parameters["communication"]["bus"], 
            mux = int(self.parameters["communication"]["mux"], 16),
            channel = self.parameters["communication"]["channel"],
            address = int(self.parameters["communication"]["address"], 16), 
            simulate = self.simulate,
        )


    @property
    def temperature(self) -> None:
        """ Gets temperature value. """
        return self.state.get_peripheral_reported_sensor_value(self.name, self.temperature_name)


    @temperature.setter
    def temperature(self, value: float) -> None:
        """ Sets temperature value in shared state. Does not update environment from calibration mode. """
        self.logger.info("Temperature: {} C".format(value))
        self.state.set_peripheral_reported_sensor_value(self.name, self.temperature_name, value)
        if self.mode != Modes.CALIBRATE:
            self.state.set_environment_reported_sensor_value(self.name, self.temperature_name, value)


    @property
    def humidity(self) -> None:
        """ Gets humidity value. """
        return self.state.get_peripheral_reported_sensor_value(self.name, self.humidity_name)


    @humidity.setter
    def humidity(self, value: float) -> None:
        """ Sets humidity value in shared state. Does not update environment from calibration mode. """
        self.logger.info("Humidity: {} %".format(value))
        self.state.set_peripheral_reported_sensor_value(self.name, self.humidity_name, value)
        if self.mode != Modes.CALIBRATE:
            self.state.set_environment_reported_sensor_value(self.name, self.humidity_name, value)


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

        # Read temperature
        temperature, error = self.sensor.read_temperature()

        # Check for errors:
        if error.exists():
            error.report("Manager unable to update")
            self.logger.warning(error.trace)
            self.mode = Modes.ERROR
            self.health = self.sensor.health.percent
            return

        # Read temperature
        humidity, error = self.sensor.read_humidity()

        # Check for errors:unix pipe an output stream gtrep
        if error.exists():
            error.report("Manager unable to update")
            self.logger.warning(error.trace)
            self.mode = Modes.ERROR
            self.health = self.sensor.health.percent
            return

        # Update reported values
        self.temperature = temperature
        self.humidity = humidity
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


    def clear_reported_values(self):
        """ Clears reported values. """
        self.temperature = None
        self.humidity = None
