# Import standard python modules
import time, json

# Import python types
from typing import Optional, Tuple, Dict, Any, List

# Import peripheral parent class
from device.peripherals.classes.peripheral import manager, modes

# Import manager elements
from device.peripherals.common.pca9633 import driver
from device.peripherals.modules.indicator_pca9633 import exceptions, events


class IndicatorPCA9633Manager(manager.PeripheralManager):
    """Manages a set of indicator leds controlled by a pca9633 led driver."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes manager."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Set default sampling interval
        self.default_sampling_interval = 3  # second
        self.prev_update = 0  # timestamp

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
            self.name, "iot_indicator_led_status"
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
        self.drivers : List[driver.PCA9633Driver] = []
        devices = self.communication.get("devices", [])
        for device in devices:
            try:
                # Initialize driver optional mux parameter
                mux = device.get("mux", None)
                if mux != None:
                    mux = int(mux, 16)

                # Initialize driver
                self.drivers.append(
                    driver.PCA9633Driver(
                        name=device.get("name", "Default"),
                        i2c_lock=self.i2c_lock,
                        bus=device["bus"],
                        mux=mux,
                        channel=device.get("channel", None),
                        address=int(device["address"], 16),
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

        # Turn off all indicator leds
        for driver in self.drivers:
          driver.set_rgb([0,0,0])

    def update_peripheral(self) -> None:
        """Updates peripheral by setting output to desired state."""
        try:
            for driver in self.drivers:
                if driver.name == "NetworkLED":
                    self.update_network_led(driver)
                elif driver.name == "IoTLED":
                    self.update_iot_led(driver)
                elif driver.name == "PeripheralLED":
                    self.update_peripheral_led(driver)
                elif driver.name == "UserLED":
                    self.update_user_led(driver)
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

    def update_network_led(self, driver: driver.PCA9633Driver) -> None:
        """Updates network indicator and status."""
        if self.network_is_connected:
            if self.network_indicator_led_status != "Green":
                driver.set_rgb([0, 32, 0])
                self.network_indicator_led_status = "Green"
        else:
            if self.network_indicator_led_status != "Red":
                driver.set_rgb([32, 0, 0])
                self.network_indicator_led_status = "Red"

    def update_iot_led(self, driver: driver.PCA9633Driver) -> None:
        """Updates iot indicator and status."""
        if self.iot_is_connected:
            if self.iot_indicator_led_status != "Green":
                driver.set_rgb([0, 32, 0])
                self.iot_indicator_led_status = "Green"
        else:
            if self.iot_indicator_led_status != "Red":
                driver.set_rgb([32, 0, 0])
                self.iot_indicator_led_status = "Red"
    
    def update_iot_and_network_led(self, driver: driver.PCA9633Driver) -> None:
        """Updates iot/network indicator and status."""
        if self.iot_is_connected:
            if self.iot_indicator_led_status != "Green":
                driver.set_rgb([0, 32, 0])
                self.iot_indicator_led_status = "Green"
        elif self.network_is_connected:
            if self.iot_indicator_led_status != "Yellow":
                driver.set_rgb([32, 32, 0])
                self.iot_indicator_led_status = "Yellow"
        else:
            if self.iot_indicator_led_status != "Red":
                driver.set_rgb([32, 0, 0])
                self.iot_indicator_led_status = "Red"

    def update_peripheral_led(self, driver: driver.PCA9633Driver) -> None:
        """Updates peripheral led indicator and status."""

        # Check if all peripherals are healthy
        healthy = True
        for _, peripheral in self.state.peripherals.items():
            if peripheral["health"] < 100:
                healthy = False

        # Update indicator led output
        if healthy:
            if self.iot_indicator_led_status != "Green":
                driver.set_rgb([0, 32, 0])
                self.iot_indicator_led_status = "Green"
        else:
            if self.iot_indicator_led_status != "Red":
                driver.set_rgb([32, 0, 0])
                self.iot_indicator_led_status = "Red"

    def update_user_led(self, driver: driver.PCA9633Driver) -> None:
        """Updates user led indicator and status."""
        driver.set_rgb([0, 32, 0])
        self.iot_indicator_led_status = "Green"
