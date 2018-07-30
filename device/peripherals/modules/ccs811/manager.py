# Import standard python modules
from typing import Optional, Tuple, Dict

# Import device utilities
from device.utilities.modes import Modes

# Import peripheral parent class
from device.peripherals.classes.peripheral_manager import PeripheralManager

# Import ccs811 elements
from device.peripherals.modules.ccs811.events import CCS811Events
from device.peripherals.modules.ccs811.driver import CCS811Driver
from device.peripherals.modules.ccs811.exceptions import DriverError


class CCS811Manager(PeripheralManager, CCS811Events):
    """ Manages an ccs811 co2 sensor. """

    def __init__(self, *args, **kwargs):
        """ Instantiates manager Instantiates parent class, and initializes 
            sensor variable name. """

        # Instantiate parent class
        super().__init__(*args, **kwargs)

        # Initialize variable names
        self.co2_name = self.parameters["variables"]["sensor"]["co2_ppm"]
        self.tvoc_name = self.parameters["variables"]["sensor"]["tvoc_ppb"]

    @property
    def co2(self) -> None:
        """ Gets co2 value. """
        return self.state.get_peripheral_reported_sensor_value(self.name, self.co2_name)

    @co2.setter
    def co2(self, value: float) -> None:
        """ Sets co2 value in shared state. Does not update environment from calibration mode. """
        self.state.set_peripheral_reported_sensor_value(self.name, self.co2_name, value)
        if self.mode != Modes.CALIBRATE:
            self.state.set_environment_reported_sensor_value(
                self.name, self.co2_name, value
            )

    @property
    def tvoc(self) -> None:
        """ Gets tvoc value. """
        return self.state.get_peripheral_reported_sensor_value(
            self.name, self.tvoc_name
        )

    @tvoc.setter
    def tvoc(self, value: float) -> None:
        """ Sets tvoc value in shared state. Does not update environment from calibration mode. """
        self.state.set_peripheral_reported_sensor_value(
            self.name, self.tvoc_name, value
        )
        if self.mode != Modes.CALIBRATE:
            self.state.set_environment_reported_sensor_value(
                self.name, self.tvoc_name, value
            )

    def initialize(self) -> None:
        """Initializes manager."""
        self.logger.info("Initializing")

        # Clear reported values
        self.clear_reported_values()

        # Initialize health
        self.health = 100.0

        # Initialize driver
        try:
            self.driver = CCS811Driver(
                name=self.name,
                bus=self.parameters["communication"]["bus"],
                mux=int(self.parameters["communication"]["mux"], 16),
                channel=self.parameters["communication"]["channel"],
                address=int(self.parameters["communication"]["address"], 16),
                simulate=self.simulate,
                mux_simulator=self.mux_simulator,
            )
        except DriverError as e:
            self.logger.exception("Manager unable to initialize")
            self.health = 0.0
            self.mode = Modes.ERROR
            return

        # Successful initialization!
        self.logger.info("Initialized successfully")

    def setup(self) -> None:
        """Sets up sensor."""
        self.logger.info("No setup required")

    def update(self) -> None:
        """Updates sensor by reading co2 and tvoc values then reports them to shared 
        state. Checks for compensation variables before read."""

        # TODO: Check for new compensation values

        # Read co2 and tvoc
        try:
            co2, tvoc = self.driver.read_algorithm_data(retry=True)
        except DriverError:
            self.logger.exception("Unable to read co2, tvoc")
            self.mode = Modes.ERROR
            self.health = 0.0
            return

        # Update reported values
        self.co2 = co2
        self.tvoc = tvoc
        self.health = 100.0

    def reset(self) -> None:
        """ Resets sensor. """
        self.logger.info("Resetting")

        # Clear reported values
        self.clear_reported_values()

        # Reset driver if not in error mode
        try:
            if self.mode != Modes.ERROR:
                self.driver.reset()
        except DriverError:
            self.logger.exception("Unable to reset driver")

        # Sucessfully reset!
        self.logger.debug("Successfully reset!")

    def shutdown(self) -> None:
        """ Shuts down sensor. """
        self.logger.info("Shutting down")

        # Clear reported values
        self.clear_reported_values()

        # Successfully shutdown
        self.logger.info("Successfully shutdown!")

    def clear_reported_values(self):
        """ Clears reported values. """
        self.co2 = None
        self.tvoc = None
