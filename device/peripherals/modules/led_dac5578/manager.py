# Import standard python modules
import threading, time

# Import python types
from typing import Optional, Tuple, Dict, Any

# Import device utilities
from device.utilities.modes import Modes

# Import peripheral parent class
from device.peripherals.classes.peripheral.manager import PeripheralManager

# Import peripheral utilities
from device.peripherals.utilities import light

# Import led elements
from device.peripherals.modules.led_dac5578.events import LEDDAC5578Events
from device.peripherals.modules.led_dac5578.driver import LEDDAC5578Driver
from device.peripherals.classes.peripheral.exceptions import DriverError


class LEDDAC5578Manager(PeripheralManager, LEDDAC5578Events):  # type: ignore
    """Manages an LED driver controlled by a dac5578."""

    prev_desired_ppfd: Optional[float] = None
    prev_desired_spectrum: Optional[Dict[str, float]] = None
    prev_desired_distance: Optional[float] = None
    prev_pulse_time: float = 0
    pulse_interval: float = 30  # seconds -> every 10 minutes

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize light driver."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize panel and channel configs
        self.panel_configs = self.communication["panels"]
        self.channel_configs = self.setup_dict["channel_configs"]

        # Initialize variable names
        self.ppfd_name = self.variables["sensor"]["ppfd_umol_m2_s"]
        self.spectrum_name = self.variables["sensor"]["spectrum_nm_percent"]
        self.distance_name = self.variables["sensor"]["illumination_distance_cm"]
        self.channel_outputs_name = self.variables["actuator"][
            "channel_output_percents"
        ]

    @property
    def spectrum(self) -> Any:
        """Gets spectrum value."""
        return self.state.get_peripheral_reported_sensor_value(
            self.name, self.spectrum_name
        )

    @spectrum.setter
    def spectrum(self, value: Optional[Dict[str, float]]) -> None:
        """Sets spectrum value in shared state."""
        self.state.set_peripheral_reported_sensor_value(
            self.name, self.spectrum_name, value
        )
        self.state.set_environment_reported_sensor_value(
            self.name, self.spectrum_name, value, simple=True
        )

    @property
    def desired_spectrum(self) -> Any:
        """Gets desired spectrum value from shared environment state if not 
        in manual mode, otherwise gets it from peripheral state."""
        if self.mode != Modes.MANUAL:
            return self.state.get_environment_desired_sensor_value(self.spectrum_name)
        else:
            return self.state.get_peripheral_desired_sensor_value(
                self.name, self.spectrum_name
            )

    @property
    def ppfd(self) -> Optional[float]:
        """Gets ppfd value."""
        value = self.state.get_peripheral_reported_sensor_value(
            self.name, self.ppfd_name
        )
        if value != None:
            return float(value)
        return None

    @ppfd.setter
    def ppfd(self, value: float) -> None:
        """Sets ppfd value in shared state."""
        self.state.set_peripheral_reported_sensor_value(
            self.name, self.ppfd_name, value
        )
        self.state.set_environment_reported_sensor_value(
            self.name, self.ppfd_name, value, simple=True
        )

    @property
    def desired_ppfd(self) -> Optional[float]:
        """Gets desired ppfd value from shared environment state if not 
        in manual mode, otherwise gets it from peripheral state."""
        if self.mode != Modes.MANUAL:
            value = self.state.get_environment_desired_sensor_value(self.ppfd_name)
            if value != None:
                return float(value)
            return None
        else:
            value = self.state.get_peripheral_reported_sensor_value(
                self.name, self.ppfd_name
            )
            if value != None:
                return float(value)
            return None

    @property
    def distance(self) -> Optional[float]:
        """Gets distance value."""
        value = self.state.get_peripheral_reported_sensor_value(
            self.name, self.distance_name
        )
        if value != None:
            return float(value)
        return None

    @distance.setter
    def distance(self, value: float) -> None:
        """Sets distance value in shared state."""
        self.state.set_peripheral_reported_sensor_value(
            self.name, self.distance_name, value
        )
        self.state.set_environment_reported_sensor_value(
            self.name, self.distance_name, value, simple=True
        )

    @property
    def desired_distance(self) -> Optional[float]:
        """Gets desired distance value from shared environment state if not 
        in manual mode, otherwise gets it from peripheral state."""
        if self.mode != Modes.MANUAL:
            value = self.state.get_environment_desired_sensor_value(self.distance_name)
            if value != None:
                return float(value)
            return None
        else:
            value = self.state.get_peripheral_reported_sensor_value(
                self.name, self.distance_name
            )
            if value != None:
                return float(value)
            return None

    @property
    def channel_outputs(self) -> Any:
        """Gets channel outputs value."""
        return self.state.get_peripheral_reported_actuator_value(
            self.name, self.channel_outputs_name
        )

    @channel_outputs.setter
    def channel_outputs(self, value: Dict[str, float]) -> None:
        """ Sets channel outputs value in shared state. """
        self.state.set_peripheral_reported_actuator_value(
            self.name, self.channel_outputs_name, value
        )
        self.state.set_environment_reported_actuator_value(
            self.channel_outputs_name, value
        )

    @property
    def desired_channel_outputs(self) -> Any:
        """ Gets desired distance value from shared environment state if not 
            in manual mode, otherwise gets it from peripheral state. """
        if self.mode != Modes.MANUAL:
            return self.state.get_environment_desired_actuator_value(
                self.channel_outputs_name
            )
        else:
            return self.state.get_peripheral_desired_actuator_value(
                self.name, self.channel_outputs_name
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
            self.driver = LEDDAC5578Driver(
                name=self.name,
                panel_configs=self.communication.get("panels"),
                channel_configs=self.setup_dict.get("channel_configs"),
                i2c_lock=self.i2c_lock,
                simulate=self.simulate,
                mux_simulator=self.mux_simulator,
            )
            self.health = 100.0 * self.driver.num_active_panels / self.driver.num_expected_panels
        except DriverError as e:
            self.logger.exception("Manager unable to initialize")
            self.health = 0.0
            self.mode = Modes.ERROR

    def setup(self) -> None:
        """Sets up manager by turning off leds."""
        self.logger.debug("Setting up")
        try:
            self.channel_outputs = self.driver.turn_off()
            self.health = 100.0 * self.driver.num_active_panels / self.driver.num_expected_panels
        except DriverError as e:
            self.logger.exception("Unable to setup")
            self.mode = Modes.ERROR
            return

        # Update reported variables
        self.update_reported_variables()

    def update(self) -> None:
        """Updates led driver if desired spectrum, ppfd, or distance value changes."""

        # Initialize update flag
        update_required = False

        # Check for new desired ppfd
        if self.desired_ppfd != None and self.desired_ppfd != self.prev_desired_ppfd:
            self.logger.info("Received new desired ppfd")
            self.logger.debug("desired_ppfd = {} Watts".format(self.desired_ppfd))
            self.distance = self.desired_distance
            update_required = True

        # Check for new desired spectrum
        if (
            self.desired_spectrum != None
            and self.desired_spectrum != self.prev_desired_spectrum
        ):
            self.logger.info("Received new desired spectrum")
            self.logger.debug("desired_spectrum = {}".format(self.desired_spectrum))
            update_required = True

        # Check for new illumination distance
        if (
            self.desired_distance != None
            and self.desired_distance != self.prev_desired_distance
        ):
            self.logger.info("Received new desired illumination distance")
            self.logger.debug("desired_distance = {} cm".format(self.desired_distance))
            update_required = True

        # Check if all desired values exist:
        all_desired_values_exist = True
        if (
            self.desired_ppfd == None
            or self.desired_spectrum == None
            or self.desired_distance == None
        ):
            all_desired_values_exist = False

        # Check for pulse timeout - must send update to device every pulse interval
        pulse_required = False
        if self.pulse_interval != None:
            pulse_delta = time.time() - self.prev_pulse_time
            if pulse_delta > self.pulse_interval:
                pulse_required = True

        # Only require update on pulse timeout if all desired values exist
        if pulse_required and all_desired_values_exist:
            update_required = True

        # Check if update is required
        if not update_required:
            return

        # Set spectral power distribution from desired values
        try:
            result = self.driver.set_spd(
                desired_distance_cm=self.desired_distance,
                desired_ppfd_umol_m2_s=self.desired_ppfd,
                desired_spectrum_nm_percent=self.desired_spectrum,
            )
            self.health = 100.0 * self.driver.num_active_panels / self.driver.num_expected_panels
        except DriverError as e:
            self.logger.exception("Unable to set spd")
            self.mode = Modes.ERROR
            self.health = 0
            return

        # Update reported values
        self.channel_outputs = result[0]
        self.spectrum = result[1]
        self.ppfd = result[2]

        # Update prev desired values
        self.prev_desired_ppfd = self.desired_ppfd
        self.prev_desired_spectrum = self.desired_spectrum
        self.prev_desired_distance = self.desired_distance

        # Update latest pulse time
        self.prev_pulse_time = time.time()

    def reset(self) -> None:
        """Resets manager."""
        self.logger.debug
        self.clear_reported_values()

    def shutdown(self) -> None:
        """Shuts down manager."""
        self.logger.debug("Shutting down")
        self.clear_reported_values()

    def clear_reported_values(self) -> None:
        """Clears reported values."""
        self.ppfd = None
        self.spectrum = None
        self.distance = None
        self.channel_outputs = None
        self.prev_desired_ppfd = None
        self.prev_desired_spectrum = None
        self.prev_desired_distance = None

    def update_reported_variables(self) -> None:
        """Updates reported variables."""

        # Get previously used distance or default setup distance
        if self.distance == None:
            self.distance = self.channel_configs[0]["planar_distance_map"][0][
                "distance_cm"
            ]

        # Get previously used spectrum or default setup spectrum for reference spd
        if self.spectrum != None:
            reference_spd = self.spectrum
        else:
            reference_spd = self.channel_configs[0]["spectrum_nm_percent"]

        # Calculate resultant spectrum and ppfd
        self.spectrum, self.ppfd = light.calculate_resultant_spd(
            channel_configs=self.channel_configs,
            reference_spd=reference_spd,
            channel_output_setpoints=self.channel_outputs,
            distance=self.distance,
        )
