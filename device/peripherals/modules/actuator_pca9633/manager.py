# Import standard python modules
import time, json, os

# Import python types
from typing import Optional, Tuple, Dict, Any, List

# Import peripheral parent class
from device.peripherals.classes.peripheral import manager, modes

# Import manager elements
from device.peripherals.common.pca9633 import driver
from device.peripherals.modules.actuator_pca9633 import exceptions, events


class ActuatorPCA9633Manager(manager.PeripheralManager):
    """Manages a set of indicator leds controlled by a pca9633 led driver."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes manager."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize colors
        self.colors = ["Red", "Green", "Yellow", "Blue", "Off"]

        # Set defaults
        self.default_sampling_interval = 3  # seconds
        self.prev_update = 0  # timestamp
        self.first_user_led_update = True
        self.previous_heartbeat_timestamp = 0
        self.heartbeat_interval = 60 # seconds

    @property
    def network_is_connected(self) -> bool:
        """Gets internet connection status."""
        return self.state.network.get("is_connected", False)

    @property
    def iot_is_connected(self) -> bool:
        """Gets value."""
        return self.state.iot.get("is_connected", False)  # type: ignore

    @property
    def network_indicator_led_status(self) -> Optional[str]:
        """Gets reported output value."""
        value = self.state.get_peripheral_reported_actuator_value(
            self.name, "network_indicator_led_status"
        )
        if value != None:
            return value
        return None

    @network_indicator_led_status.setter
    def network_indicator_led_status(self, value: bool) -> None:
        """Sets reported output value in shared state."""
        self.state.set_peripheral_reported_actuator_value(
            self.name, "network_indicator_led_status", value
        )
        self.state.set_environment_reported_actuator_value(
            "network_indicator_led_status", value
        )
        self.state.set_environment_desired_actuator_value(
            "network_indicator_led_status", value
        )

    @property
    def iot_indicator_led_status(self) -> Optional[str]:
        """Gets reported output value."""
        value = self.state.get_peripheral_reported_actuator_value(
            self.name, "iot_indicator_led_status"
        )
        if value != None:
            return value
        return None

    @iot_indicator_led_status.setter
    def iot_indicator_led_status(self, value: bool) -> None:
        """Sets reported output value in shared state."""
        self.state.set_peripheral_reported_actuator_value(
            self.name, "iot_indicator_led_status", value
        )
        self.state.set_environment_reported_actuator_value(
            "iot_indicator_led_status", value
        )
        self.state.set_environment_desired_actuator_value(
            "iot_indicator_led_status", value
        )

    @property
    def peripheral_indicator_led_status(self) -> Optional[str]:
        """Gets reported output value."""
        value = self.state.get_peripheral_reported_actuator_value(
            self.name, "peripheral_indicator_led_status"
        )
        if value != None:
            return value
        return None

    @peripheral_indicator_led_status.setter
    def peripheral_indicator_led_status(self, value: bool) -> None:
        """Sets reported output value in shared state."""
        self.state.set_peripheral_reported_actuator_value(
            self.name, "peripheral_indicator_led_status", value
        )
        self.state.set_environment_reported_actuator_value(
            "peripheral_indicator_led_status", value
        )
        self.state.set_environment_desired_actuator_value(
            "peripheral_indicator_led_status", value
        )

    @property
    def user_indicator_led_status(self) -> Optional[str]:
        """Gets reported output value."""
        value = self.state.get_peripheral_reported_actuator_value(
            self.name, "user_indicator_led_status"
        )
        if value != None:
            return value
        return None

    @user_indicator_led_status.setter
    def user_indicator_led_status(self, value: bool) -> None:
        """Sets reported output value in shared state."""
        self.state.set_peripheral_reported_actuator_value(
            self.name, "user_indicator_led_status", value
        )
        self.state.set_environment_reported_actuator_value(
            "user_indicator_led_status", value
        )
        self.state.set_environment_desired_actuator_value(
            "user_indicator_led_status", value
        )

    def initialize_peripheral(self) -> None:
        """Initializes manager."""
        self.logger.info("Initializing")

        # Clear reported values
        self.clear_reported_values()

        # Initialize health
        self.health = 100.0

        # Initialize drivers
        self.drivers: List[driver.PCA9633Driver] = []
        devices = self.communication.get("devices", [])
        with self.i2c_lock:
            for device in devices:
                try:
                    # Initialize bus
                    bus = device.get("bus")
                    if bus == "default":
                        self.logger.debug("Using default i2c bus")
                        bus = os.getenv("DEFAULT_I2C_BUS")
                    if bus == "none":
                      bus = None
                    if bus != None:
                        bus = int(bus)

                    # Initialize mux
                    mux = device.get("mux")
                    if mux == "default":
                        self.logger.debug("Using default i2c mux")
                        mux = os.getenv("DEFAULT_MUX_ADDRESS")
                    if mux == "none":
                      mux = None
                    if mux != None:
                        mux = int(mux, 16)

                    # Initialize i2c channel
                    channel = device.get("channel")

                    # Initialize i2c address
                    address = device.get("address")
                    if address != None:
                        address = int(address, 16)

                    # Initialize driver
                    self.drivers.append(
                        driver.PCA9633Driver(
                            name=device.get("name", "Default"),
                            i2c_lock=self.i2c_lock,
                            bus=bus,
                            mux=mux,
                            channel=channel,
                            address=address,
                            simulate=self.simulate,
                            mux_simulator=self.mux_simulator,
                        )
                    )
                except exceptions.DriverError as e:
                    self.logger.exception("Unable to initialize: {}".format(e))
                    self.health = 0.0
                    self.mode = modes.ERROR

    def setup_peripheral(self) -> None:
        """Sets up peripheral."""
        self.logger.debug("No setup required for peripheral")

        # Turn off leds
        for driver in self.drivers:
            driver.set_rgb([0, 0, 0])
        
        # Update indicator status
        self.peripheral_indicator_led_status = "Off"
        self.network_indicator_led_status = "Off"
        self.iot_indicator_led_status = "Off"
        self.user_indicator_led_status = "Off"

    def update_peripheral(self) -> None:
        """Updates peripheral by setting output to desired state."""

        # Check for heartbeat
        send_heartbeat = False
        current_timestamp = time.time()
        if current_timestamp - self.previous_heartbeat_timestamp > self.heartbeat_interval:
            self.previous_heartbeat_timestamp = current_timestamp
            send_heartbeat = True
            self.logger.debug("Sending heartbeat")

        # Update each driver
        try:
            for driver in self.drivers:
                if driver.name == "NetworkLED":
                    self.update_network_led(driver, send_heartbeat)
                elif driver.name == "IoTLED":
                    self.update_iot_led(driver, send_heartbeat)
                elif driver.name == "PeripheralLED":
                    self.update_peripheral_led(driver, send_heartbeat)
                elif driver.name == "UserLED":
                    self.update_user_led(driver, send_heartbeat)
        except exceptions.DriverError as e:
            self.logger.exception("Unable to update peripheral: {}".format(e))
            self.mode = modes.ERROR
            self.health = 0.0

    def reset_peripheral(self) -> None:
        """Resets sensor."""
        self.logger.info("Resetting")
        try:
            for driver in self.drivers:
                driver.set_rgb([0, 0, 0])  # off
        except exceptions.DriverError as e:
            message = "Unable to turn off indicator before shutting down: {}".format(
                type(e)
            )
            self.logger.warning(message)
        self.clear_reported_values()

    def shutdown_peripheral(self) -> None:
        """Shutsdown peripheral."""
        self.logger.info("Shutting down")
        try:
            for driver in self.drivers:
                driver.set_rgb([0, 0, 0])  # off
        except exceptions.DriverError as e:
            message = "Unable to turn off indicator before shutting down: {}".format(
                type(e)
            )
            self.logger.warning(message)
        self.clear_reported_values()

    def clear_reported_values(self) -> None:
        """Clears reported values."""
        self.network_indicator_led_status = None
        self.iot_indicator_led_status = None
        self.peripheral_indicator_led_status = None
        self.user_indicator_led_status = None

    ##### HELPER METHODS ###############################################################

    def update_network_led(self, driver: driver.PCA9633Driver, send_heartbeat: bool = False) -> None:
        """Updates network indicator and status."""
        if self.network_is_connected:
            if self.network_indicator_led_status != "Green" or send_heartbeat:
                self.logger.debug("Setting network led green")
                driver.set_rgb([0, 32, 0])
                self.network_indicator_led_status = "Green"
        else:
            if self.network_indicator_led_status != "Red" or send_heartbeat:
                self.logger.debug("Setting network led red")
                driver.set_rgb([32, 0, 0])
                self.network_indicator_led_status = "Red"

    def update_iot_led(self, driver: driver.PCA9633Driver, send_heartbeat: bool = False) -> None:
        """Updates iot indicator and status."""
        if self.iot_is_connected:
            if self.iot_indicator_led_status != "Green" or send_heartbeat:
                self.logger.debug("Setting iot led green")
                driver.set_rgb([0, 32, 0])
                self.iot_indicator_led_status = "Green"
        else:
            if self.iot_indicator_led_status != "Red" or send_heartbeat:
                self.logger.debug("Setting iot led red")
                driver.set_rgb([32, 0, 0])
                self.iot_indicator_led_status = "Red"


    def update_peripheral_led(self, driver: driver.PCA9633Driver, send_heartbeat: bool = False) -> None:
        """Updates peripheral led indicator and status."""

        # Check if all peripherals are setup and healthy
        healthy = True
        setup = True
        for _, peripheral in self.state.peripherals.items():

            # Check mode
            mode = peripheral.get("mode")
            if mode == modes.INIT or mode == modes.SETUP:
                setup = False
                break

            # Check health
            health = peripheral.get("health")
            if health < 100:
                healthy = False

        # Update indicator led output
        if not setup:
            if self.peripheral_indicator_led_status != "Yellow" or send_heartbeat:
                self.logger.debug("Setting peripheral led yellow")
                driver.set_rgb([32, 32, 0])
                self.peripheral_indicator_led_status = "Yellow"
        elif healthy:
            if self.peripheral_indicator_led_status != "Green" or send_heartbeat:
                self.logger.debug("Setting peripheral led green")
                driver.set_rgb([0, 32, 0])
                self.peripheral_indicator_led_status = "Green"
        else:
            if self.peripheral_indicator_led_status != "Red" or send_heartbeat:
                self.logger.debug("Setting peripheral led red")
                driver.set_rgb([32, 0, 0])
                self.peripheral_indicator_led_status = "Red"

    def update_user_led(self, driver: driver.PCA9633Driver, send_heartbeat: bool = False) -> None:
        """Updates user led indicator and status."""

        # Set green on first update
        if self.first_user_led_update:
            self.first_user_led_update = False
            self.logger.debug("Setting user led green")
            driver.set_rgb([0, 32, 0])
            self.user_indicator_led_status = "Green"

        # Check to send heartbeat
        elif send_heartbeat:
            if self.user_indicator_led_status == "Green": 
                self.logger.debug("Setting user led green")
                driver.set_rgb([0, 32, 0])
            elif self.user_indicator_led_status == "Yellow":
                self.logger.debug("Setting user led yellow")
                driver.set_rgb([32, 32, 0])
            elif self.user_indicator_led_status == "Red":
                self.logger.debug("Setting user led red")
                driver.set_rgb([32, 0, 0])
            elif self.user_indicator_led_status == "Blue":
                self.logger.debug("Setting user led blue")
                driver.set_rgb([0, 0, 32])
            elif self.user_indicator_led_status == "Off":
                self.logger.debug("Setting user led off")
                driver.set_rgb([0, 0, 0])


 ##### EVENT FUNCTIONS ##############################################################

    def create_peripheral_specific_event(
        self, request: Dict[str, Any]
    ) -> Tuple[str, int]:
        """Processes peripheral specific event."""
        if request["type"] == events.SET_USER_LED:
            return self.set_user_led(request)
        else:
            return "Unknown event request type", 400

    def check_peripheral_specific_events(self, request: Dict[str, Any]) -> None:
        """Checks peripheral specific events."""
        if request["type"] == events.SET_USER_LED:
            self._set_user_led(request)
        else:
            message = "Invalid event request type in queue: {}".format(request["type"])
            self.logger.error(message)

    def set_user_led(self,request: Dict[str, Any]) -> Tuple[str, int]:
        """Pre-processes set user led event request."""
        self.logger.debug("Pre-processing set user led request")

        # Get request parameters
        color = request.get("value")

        # Validate parameters
        if color not in self.colors:
          return "Invalid color, must be Red, Green, Blue, Yellow, or Off", 400

        # Add event request to event queue
        request = {"type": events.SET_USER_LED, "color": color}
        self.event_queue.put(request)

        # Successfully turned on
        return f"Setting user LED {color}", 200

    def _set_user_led(self, request: Dict[str, Any]) -> None:
        """Processes turn on event request."""
        self.logger.debug("Processing set led event request")

        # Get request parameters
        color = request.get("color")

        # Set user led and update reported variables
        try:
            self.user_indicator_led_status = color
            for driver in self.drivers:
                if driver.name == "UserLED":
                    if color == "Green": 
                        self.logger.debug("Setting user led green")
                        driver.set_rgb([0, 32, 0])
                    elif color == "Yellow":
                        self.logger.debug("Setting user led yellow")
                        driver.set_rgb([32, 32, 0])
                    elif color == "Red":
                        self.logger.debug("Setting user led red")
                        driver.set_rgb([32, 0, 0])
                    elif color == "Blue":
                        self.logger.debug("Setting user led blue")
                        driver.set_rgb([0, 0, 32])
                    elif color == "Off":
                        self.logger.debug("Setting user led blue")
                        driver.set_rgb([0, 0, 0])
                    break
            
        except exceptions.DriverError as e:
            self.mode = modes.ERROR
            message = "Unable to set user led: {}".format(e)
            self.logger.debug(message)
        except:
            self.mode = modes.ERROR
            message = "Unable to set user led, unhandled exception"
            self.logger.exception(message)