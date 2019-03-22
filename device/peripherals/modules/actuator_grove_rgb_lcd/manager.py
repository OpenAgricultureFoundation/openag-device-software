# Import standard python modules
import time

# Import python types
from typing import Optional, Tuple, Dict, Any

# Import peripheral parent class
from device.peripherals.classes.peripheral import manager, modes

# Import manager elements
from device.peripherals.modules.actuator_grove_rgb_lcd import exceptions, events, driver


class ActuatorGroveRGBLCDManager(manager.PeripheralManager):
    """Manages an actuator controlled by a Grove RGB LCD."""

    # --------------------------------------------------------------------------
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes manager."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize communication variables
        self.rgb_address = self.communication.get("rgb_address")
        self.lcd_address = self.communication.get("lcd_address")

        # Get setup defaults
        comms = {}
        if self.setup_dict is not None:
            params = self.setup_dict.get("parameters")
            if params is not None:
                comms = params.get("communication")

        # Try to get settings from setup file, if they are not in peripheral
        if self.rgb_address is None:
            rgb = comms.get("rgb_address")
            if rgb is not None:
                self.rgb_address = rgb.get("default")
        if self.lcd_address is None:
            lcd = comms.get("lcd_address")
            if lcd is not None:
                self.lcd_address = lcd.get("default")

        if self.rgb_address is None:
            self.logger.critical("Missing RGB I2C address")
            return
        if self.lcd_address is None:
            self.logger.critical("Missing LCD I2C address")
            return

        # Convert i2c config params from hex to int if they exist
        self.rgb_address = int(self.rgb_address, 16)
        self.lcd_address = int(self.lcd_address, 16)

        if self.bus is None:
            self.bus = self.communication.get("bus")
            if self.bus is not None:
                self.bus = int(self.bus)
        if self.mux is None:
            self.mux = self.communication.get("mux")
            if self.mux is not None:
                self.mux = int(self.mux, 16)

        self.logger.info(
            "rgb_address=0x{:02X}, lcd_address=0x{:02X}".format(
                self.rgb_address, self.lcd_address
            )
        )

        # Initialize variable names
        self.temperature_sensor = None
        self.humidity_sensor = None
        sensor = self.variables.get("sensor")
        if sensor is not None:
            self.temperature_sensor = sensor.get("temperature_celsius")
            self.humidity_sensor = sensor.get("humidity_percent")
        if self.temperature_sensor is None or self.humidity_sensor is None:
            self.logger.critical("Missing sensor names")
            return

        # Set default sampling interval and heartbeat
        self.default_sampling_interval = 5  # seconds
        self.heartbeat = 60  # seconds
        self.prev_update = 0  # timestamp

    # --------------------------------------------------------------------------
    def initialize_peripheral(self) -> None:
        """Initializes manager."""
        self.logger.info("Initializing")

        # Initialize health
        self.health = 100.0

        # Initialize driver
        try:
            self.driver = driver.GroveRGBLCDDriver(
                name=self.name,
                i2c_lock=self.i2c_lock,
                bus=self.bus,
                rgb_address=self.rgb_address,
                lcd_address=self.lcd_address,
                mux=self.mux,
                channel=self.channel,
                simulate=self.simulate,
                mux_simulator=self.mux_simulator,
            )
        except exceptions.DriverError as e:
            self.logger.exception("Unable to initialize: {}".format(e))
            self.health = 0.0
            self.mode = modes.ERROR

    # --------------------------------------------------------------------------
    def setup_peripheral(self) -> None:
        """Sets up peripheral."""
        self.logger.debug("Setting up peripheral")
        try:
            self.driver.write_string("setup")
        except exceptions.DriverError as e:
            self.logger.exception("Unable to setup: {}".format(e))
            self.mode = modes.ERROR
            self.health = 0.0

    # --------------------------------------------------------------------------
    def update_peripheral(self) -> None:
        """Updates peripheral by setting output to desired state."""
        try:
            # Check for heartbeat
            if time.time() - self.prev_update > self.heartbeat:
                self.logger.debug("Sending heartbeat")
                self.set_output()

        except exceptions.DriverError as e:
            self.logger.exception("Unable to update peripheral: {}".format(e))
            self.mode = modes.ERROR
            self.health = 0.0

    # --------------------------------------------------------------------------
    def reset_peripheral(self) -> None:
        """Resets sensor."""
        self.logger.info("Resetting")

    # --------------------------------------------------------------------------
    def shutdown_peripheral(self) -> None:
        """Shutsdown peripheral."""
        self.logger.info("Shutting down")

    ##### HELPER FUNCTIONS ####################################################

    # --------------------------------------------------------------------------
    def set_output(self):
        """Gets desired output value from input sensor values."""
        tempC = self.state.get_environment_reported_sensor_value(
            self.temperature_sensor
        )
        hum = self.state.get_environment_reported_sensor_value(self.humidity_sensor)
        if tempC is None:
            return

        tempF = float(tempC) * 1.8 + 32.0
        lt = time.localtime()
        lt = time.strftime("%H:%M:%S", lt)
        output = "{}C / {}F\n{} %RH {}".format(tempC, tempF, hum, lt)
        self.logger.debug("Output: {}".format(output))

        # backlight color based on temp
        if tempF <= 65:
            self.driver.set_backlight(R=0x00, G=0x00, B=0xFF)
            self.logger.debug("Cold")
        if tempF > 65 and tempF < 80:
            self.driver.set_backlight(R=0x00, G=0xFF, B=0x00)
            self.logger.debug("Comfortable")
        if tempF >= 80:
            self.driver.set_backlight(R=0xFF, G=0x00, B=0x00)
            self.logger.debug("Hot")

        self.driver.write_string(output)
        self.prev_update = time.time()

    # --------------------------------------------------------------------------
    def display_time(self):
        """Shows the current time."""
        self.logger.debug("display time")
        self.driver.display_time()

    ##### EVENT FUNCTIONS #####################################################

    # --------------------------------------------------------------------------
    def create_peripheral_specific_event(
        self, request: Dict[str, Any]
    ) -> Tuple[str, int]:
        """Processes peripheral specific event."""
        if request["type"] == events.DISPLAY_TIME:
            return self.show_time()
        else:
            return "Unknown event request type", 400

    # --------------------------------------------------------------------------
    def check_peripheral_specific_events(self, request: Dict[str, Any]) -> None:
        """Checks peripheral specific events."""
        if request["type"] == events.DISPLAY_TIME:
            self._show_time()
        else:
            message = "Invalid event request type in queue: {}".format(request["type"])
            self.logger.error(message)

    # --------------------------------------------------------------------------
    def show_time(self) -> Tuple[str, int]:
        """Pre-processes display time event request."""
        self.logger.debug("Pre-processing display time event request")

        # Require mode to be in manual
        if self.mode != modes.MANUAL:
            return "Must be in manual mode", 400

        # Add event request to event queue
        request = {"type": events.DISPLAY_TIME}
        self.event_queue.put(request)

        # Successful
        return "Displaying time", 200

    # --------------------------------------------------------------------------
    def _show_time(self) -> None:
        self.logger.debug("Processing display time event request")

        # Require mode to be in manual
        if self.mode != modes.MANUAL:
            self.logger.critical("Tried to display time from {} mode".format(self.mode))

        try:
            self.display_time()
        except exceptions.DriverError as e:
            self.mode = modes.ERROR
            message = "Unable to display time: {}".format(e)
            self.logger.debug(message)
        except:
            self.mode = modes.ERROR
            message = "Unable to display time, unhandled exception"
            self.logger.exception(message)
