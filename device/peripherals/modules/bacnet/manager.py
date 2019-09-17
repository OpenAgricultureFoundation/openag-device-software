# Import standard python modules
import time

# Import python types
from typing import Optional, Tuple, Dict, Any

# Import peripheral parent class
from device.peripherals.classes.peripheral import manager, modes

# Import manager elements
from device.peripherals.modules.bacnet import exceptions, events, driver

class BacnetManager(manager.PeripheralManager):
    """Manages an HVAC actuator controlled by BACNet device."""

    # --------------------------------------------------------------------------
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes manager."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        self.driver = None

        # Read our own set up files here, since we don't use I2C like the 
        # base peripheral class does
        self.bacpypes_ini_file = self.properties.get("bacpypes_ini_file")
        self.bacnet_config_file = self.properties.get("bacnet_config")
        self.debug = self.properties.get("debug")

        # Verify props
        if self.setup_dict is None or self.bacpypes_ini_file is None or \
                self.bacnet_config_file is None:
            self.logger.critical("Missing mandatory properties.")
            return
        self.logger.info(f"bacpypes_ini_file={self.bacpypes_ini_file}")
        self.logger.info(f"bacnet_config_file={self.bacnet_config_file}")

        # Initialize variable names
        self.temperature_name = self.variables["sensor"]["temperature_celsius"]
        self.humidity_name = self.variables["sensor"]["humidity_percent"]

        # Set default sampling interval 
        self.default_sampling_interval = 60  # seconds

    # --------------------------------------------------------------------------
    def initialize_peripheral(self) -> None:
        """Initializes manager."""
        self.logger.info("Initializing")

        # Initialize health
        self.health = 100.0

        # Initialize driver
        try:
            if self.driver is None:
                self.driver = driver.BacnetDriver(
                    name=self.name,
                    simulate=self.simulate,
                    ini_file=self.bacpypes_ini_file,
                    config_file=self.bacnet_config_file,
                    debug=self.debug)
        except exceptions.DriverError as e:
            self.logger.exception(f"Unable to initialize: {e}")
            self.health = 0.0
            self.mode = modes.ERROR

    # --------------------------------------------------------------------------
    def setup_peripheral(self) -> None:
        """Sets up peripheral."""
        self.logger.debug("Setting up peripheral")
        try:
            self.driver.setup()
        except exceptions.DriverError as e:
            self.logger.exception(f"Unable to setup: {e}")
            self.mode = modes.ERROR
            self.health = 0.0

    # --------------------------------------------------------------------------
    # Called every sampling interval
    def update_peripheral(self) -> None:
        """Updates peripheral by setting output to desired state."""
        try:
            # Get the DESIRED values (set by recipe) and send them to the 
            # bacnet device that sets the setpoint for the HVAC.
            tempC = self.state.get_environment_desired_sensor_value(
                self.temperature_name)
            self.logger.info(f"Set point tempC={tempC}")
            self.driver.set_air_temp(tempC)

            RH = self.state.get_environment_desired_sensor_value(
                self.humidity_name)
            self.logger.info(f"Set point RH={RH}")
            self.driver.set_air_RH(RH)

            # Set temp & RH environment variables that will be published
            tempC = self.driver.get_air_temp()
            self.logger.info(f"Sensed tempC={tempC}")
            self.state.set_peripheral_reported_sensor_value(
                self.name, self.temperature_name, tempC)
 
            RH = self.driver.get_air_temp()
            self.logger.info(f"Sensed RH={RH}")
            self.state.set_peripheral_reported_sensor_value(
                self.name, self.humidity_name, RH)
 

        except exceptions.DriverError as e:
            self.logger.exception(f"Unable to update peripheral: {e}")
            self.mode = modes.ERROR
            self.health = 0.0

    # --------------------------------------------------------------------------
    def reset_peripheral(self) -> None:
        self.logger.info("Resetting")
        self.driver.reset()

    # --------------------------------------------------------------------------
    def shutdown_peripheral(self) -> None:
        self.logger.info("Shutting down")
        self.driver.shutdown()

    # --------------------------------------------------------------------------
    def enable_calibration_mode(self) -> Tuple[str, int]:
        return "Calibration not possible for this peripheral", 200


    ##### EVENT FUNCTIONS #####################################################

    # --------------------------------------------------------------------------
    def create_peripheral_specific_event(
        self, request: Dict[str, Any]
    ) -> Tuple[str, int]:
        """Processes peripheral specific event."""
        if self.mode != modes.MANUAL:
            return f"Must be in MANUAL mode, peripheral is in {self.mode}.", 400

        if request["type"] == events.WHOIS_PING:
            self.event_queue.put(request)
            return "Pinging bacnet devices", 200
        elif request["type"] == events.SET_TEST_V:
            try:
                volts_percent = float(request.get('value', '-1.0'))
            except:
                volts_percent = -1.0
            if volts_percent < 0.0 or volts_percent > 100.0:
                return f"Please enter a value between 0 and 100 percent.", 400
            request["value"] = volts_percent
            self.event_queue.put(request)
            return f"Setting test volts_percent to {request.get('value')} %", 200
        elif request["type"] == events.SET_AIR_TEMP:
            try:
                tempC = float(request.get('value', '-200.0'))
            except:
                tempC = -200.0
            if tempC < -100.0 or tempC > 200.0:
                return f"Please enter a value between -100 and 200 C.", 400
            request["value"] = tempC
            self.event_queue.put(request)
            return f"Setting air temp to {request.get('value')} C", 200
        elif request["type"] == events.SET_AIR_RH:
            try:
                RH = float(request.get('value', '-1.0'))
            except:
                RH = -1.0
            if RH < 0 or RH > 100.0:
                return f"Please enter a value between 0 and 100 %.", 400
            request["value"] = RH
            self.event_queue.put(request)
            return f"Setting air RH to {request.get('value')} %", 200
        else:
            return f"Unknown event request type {request.get('type')}", 400

    # --------------------------------------------------------------------------
    def check_peripheral_specific_events(self, request: Dict[str, Any]) -> None:
        """Checks peripheral specific events."""
        try:
            if request["type"] == events.WHOIS_PING:
                self.driver.ping()
            elif request["type"] == events.SET_TEST_V:
                self.driver.set_test_voltage(request.get("value"))
            elif request["type"] == events.SET_AIR_TEMP:
                self.driver.set_air_temp(request.get("value"))
            elif request["type"] == events.SET_AIR_RH:
                self.driver.set_air_RH(request.get("value"))
            else:
                self.logger.error( 
                    f"Invalid event request type: {request['type']}")
        except exceptions.DriverError as e:
            self.mode = modes.ERROR
            self.logger.debug(f"Driver Error: {e}")
        except:
            self.mode = modes.ERROR
            self.logger.exception(f"Unhandled exception in bacnet {request}")

