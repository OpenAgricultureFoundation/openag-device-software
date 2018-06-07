# Import standard python modules
from typing import Optional, Tuple, Dict, NamedTuple

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.health import Health
from device.utilities.error import Error

# Import peripheral parent class
from device.peripherals.classes.peripheral_manager import PeripheralManager

# Import led array and events
from device.peripherals.modules.t6713.sensor import T6713Sensor
from device.peripherals.modules.t6713.events import T6713Events


class T6713(PeripheralManager, T6713Events):
    """ Manages a t6713 carbon dioxide sensor. """


    def __init__(self, *args, **kwargs):
        """ Instantiates manager Instantiates parent class, and initializes 
            sensor variable name. """

        # Instantiate parent class
        super().__init__(*args, **kwargs)

        # Initialize variable names
        self.carbon_dioxide_name = self.parameters["variables"]["sensor"]["carbon_dioxide_ppm"]

        # Initialize sensor
        self.sensor = T6713Sensor(
            name = self.name, 
            bus = self.parameters["communication"]["bus"], 
            mux = int(self.parameters["communication"]["mux"], 16),
            channel = self.parameters["communication"]["channel"],
            address = int(self.parameters["communication"]["address"], 16), 
            simulate = self.simulate,
        )


    @property
    def carbon_dioxide(self) -> None:
        """ Gets carbon dioxide value. """
        return self.state.get_peripheral_reported_sensor_value(self.name, self.carbon_dioxide_name)


    @carbon_dioxide.setter
    def carbon_dioxide(self, value: float) -> None:
        """ Sets carbon dioxide value in shared state. Does not update enironment from calibration mode. """
        self.state.set_peripheral_reported_sensor_value(self.name, self.carbon_dioxide_name, value)
        if self.mode != Modes.CALIBRATE:
            self.state.set_environment_reported_sensor_value(self.name, self.carbon_dioxide_name, value)


    def initialize(self) -> None:
        """ Initializes manager."""
        self.logger.info("Initializing")

        # Clear reported values
        self.clear_reported_values()

        # Initialize health
        self.health = self.sensor.health.percent

        # Initialize sensor
        error = self.sensor.initialize()

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

        # Read carbon_dioxide
        co2, error = self.sensor.read_carbon_dioxide()

        # Check for errors:
        if error.exists():
            error.report("Manager unable to update")
            self.logger.warning(error.trace)
            self.mode = Modes.ERROR
            self.health = self.sensor.health.percent
            return

        # Update reported values
        self.carbon_dioxide = co2
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
        self.carbon_dioxide = None
