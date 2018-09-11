# Import standard python modules
import time, threading

# Import python types
from typing import NamedTuple, Optional, Tuple, Dict, Any, List

# Import device utilities
from device.utilities.logger import Logger

# Import mux simulator
from device.comms.i2c2.mux_simulator import MuxSimulator

# Import peripheral utilities
from device.peripherals.utilities import light

# Import dac driver elements
from device.peripherals.common.dac5578.driver import DAC5578Driver

# Import exceptions
from device.peripherals.classes.peripheral.exceptions import (
    DriverError,
    InitError,
    SetupError,
)
from device.peripherals.modules.led_dac5578.exceptions import (
    NoActivePanelsError,
    TurnOnError,
    TurnOffError,
    SetSPDError,
    SetOutputError,
    SetOutputsError,
    InvalidChannelNameError,
)


# TODO: Might want to scale outputs here, instead of utilities/light.py...or pass to DAC

# def scale_channel_logic(
#     channel_logic_list: List[float], logic_scaler: Dict[str, float]
# ) -> List[float]:
#     """Scales channel logic to setpoints."""

#     # Build interpolation lists
#     logic_list = []
#     setpoint_list = []
#     for logic, setpoint in logic_scaler.items():
#         logic_list.append(float(logic))
#         setpoint_list.append(float(setpoint))

#     # Build channel setpoint list
#     channel_setpoint_list = []
#     for channel_logic in channel_logic_list:
#         channel_setpoint = maths.interpolate(logic_list, setpoint_list, channel_logic)
#         channel_setpoint_list.append(channel_setpoint)

#     # Successfully built channel setpoint list
#     return channel_setpoint_list


# def test_scale_channel_logic() -> None:
#     channel_logic_list = [0, 37.5, 62.5, 87.5, 100]
#     logic_scaler = {"0": 0, "25": 10, "50": 30, "75": 60, "100": 90}
#     expected = [0, 20, 45, 75, 90]
#     channel_setpoint_list = light.scale_channel_logic(channel_logic_list, logic_scaler)
#     assert channel_setpoint_list == expected


class LEDDAC5578Panel(object):
    """An led panel controlled by a dac5578."""

    # Initialize var defaults
    is_shutdown: bool = True
    driver: Optional[DAC5578Driver] = None

    def __init__(
        self,
        driver_name: str,
        config: Dict[str, Any],
        i2c_lock: threading.Lock,
        simulate: bool,
        mux_simulator: Optional[MuxSimulator],
        logger: Logger,
    ) -> None:
        """Initializes panel."""

        # Initialize panel parameters
        self.driver_name = driver_name
        self.name = str(config.get("name"))
        self.full_name = driver_name + "-" + self.name
        self.bus = config.get("bus")
        self.address = int(config.get("address"), 16)  # type: ignore
        self.active_low = config.get("active_low")
        self.i2c_lock = i2c_lock
        self.simulate = simulate
        self.mux_simulator = mux_simulator
        self.logger = logger

        # Initialize i2c mux address
        self.mux = config.get("mux")
        if self.mux != None:
            self.mux = int(self.mux, 16)  # type: ignore

        # Initialize i2c channel value
        self.channel = config.get("channel")
        if self.channel != None:
            self.channel = int(self.channel)  # type: ignore

    def initialize(self) -> None:
        """Initializes panel."""
        self.logger.debug("Initializing {}".format(self.name))
        try:
            self.driver = DAC5578Driver(
                name=self.full_name,
                i2c_lock=self.i2c_lock,
                bus=self.bus,
                address=self.address,
                mux=self.mux,
                channel=self.channel,
                simulate=self.simulate,
                mux_simulator=self.mux_simulator,
            )
            self.is_shutdown = False
        except Exception as e:
            self.logger.exception("Unable to initialize `{}`".format(self.name))
            self.is_shutdown = True


class LEDDAC5578Driver:
    """Driver for array of led panels controlled by a dac5578."""

    # Initialize var defaults
    num_active_panels = 0
    num_expected_panels = 1

    def __init__(
        self,
        name: str,
        panel_configs: List[Dict[str, Any]],
        channel_configs: Dict[str, Any],
        i2c_lock: threading.Lock,
        simulate: bool = False,
        mux_simulator: Optional[MuxSimulator] = None,
    ) -> None:
        """Initializes driver."""

        # Initialize driver parameters
        self.channel_configs = channel_configs
        self.i2c_lock = i2c_lock
        self.simulate = simulate

        # Initialize logger
        self.logger = Logger(name="Driver({})".format(name), dunder_name=__name__)

        # Initialze num expected panels
        self.num_expected_panels = len(panel_configs)

        # Initialize panels
        self.panels: List[LEDDAC5578Panel] = []
        for config in panel_configs:
            panel = LEDDAC5578Panel(
                name, config, i2c_lock, simulate, mux_simulator, self.logger
            )
            panel.initialize()
            self.panels.append(panel)

        # Check at least one panel is still active
        active_panels = [panel for panel in self.panels if not panel.is_shutdown]
        self.num_active_panels = len(active_panels)
        if self.num_active_panels < 1:
            raise NoActivePanelsError(logger=self.logger)

        # Successfully initialized
        message = "Successfully initialized with {} ".format(self.num_active_panels)
        message2 = "active panels, expected {}".format(self.num_expected_panels)
        self.logger.debug(message + message2)

    def turn_on(self) -> Dict[str, float]:
        """Turns on leds."""
        self.logger.debug("Turning on")
        channel_outputs = self.build_channel_outputs(100)
        self.set_outputs(channel_outputs)
        return channel_outputs

    def turn_off(self) -> Dict[str, float]:
        """Turns off leds."""
        self.logger.debug("Turning off")
        channel_outputs = self.build_channel_outputs(0)
        self.set_outputs(channel_outputs)
        return channel_outputs

    def set_spd(
        self,
        desired_distance_cm: float,
        desired_ppfd_umol_m2_s: float,
        desired_spectrum_nm_percent: Dict,
    ) -> Tuple[Optional[Dict], Optional[Dict], Optional[Dict]]:
        """Sets spectral power distribution."""
        message = "Setting spd, distance={}cm, ppfd={}umol/m2/s, spectrum={}".format(
            desired_distance_cm, desired_ppfd_umol_m2_s, desired_spectrum_nm_percent
        )
        self.logger.debug(message)

        # Approximate spectral power distribution
        try:
            channel_outputs, output_spectrum_nm_percent, output_ppfd_umol_m2_s = light.approximate_spd(
                channel_configs=self.channel_configs,
                desired_distance_cm=desired_distance_cm,
                desired_ppfd_umol_m2_s=desired_ppfd_umol_m2_s,
                desired_spectrum_nm_percent=desired_spectrum_nm_percent,
            )
        except Exception as e:
            message = "approximate spd failed"
            raise SetSPDError(message=message, logger=self.logger) from e

        # Check at least one panel is active
        active_panels = [panel for panel in self.panels if not panel.is_shutdown]
        if len(active_panels) < 1:
            raise NoActivePanelsError(logger=self.logger)

        # Set outputs on each active panel
        for panel in active_panels:
            try:
                self.set_outputs(channel_outputs)
            except Exception as e:
                self.logger.exception("Unable to set output on {}".format(panel.name))

        # Check at least one panel is still active
        active_panels = [panel for panel in self.panels if not panel.is_shutdown]
        if len(active_panels) < 1:
            message = "failed when setting spd"
            raise NoActivePanelsError(message=message, logger=self.logger)

        # Successfully set channel outputs
        self.logger.debug(
            "Successfully set spd, output: channels={}, spectrum={}, ppfd={}umol/m2/s".format(
                channel_outputs, output_spectrum_nm_percent, output_ppfd_umol_m2_s
            )
        )
        return (channel_outputs, output_spectrum_nm_percent, output_ppfd_umol_m2_s)

    def set_outputs(self, outputs: dict) -> None:
        """Sets outputs on dac. Converts channel names to channel numbers 
        then sets outputs on dac."""
        self.logger.debug("Setting outputs: {}".format(outputs))

        # Convert channel names to channel numbers
        converted_outputs = {}
        for name, percent in outputs.items():

            # Convert channel name to channel number
            try:
                number = self.get_channel_number(name)
            except Exception as e:
                raise SetOutputsError(logger=self.logger) from e

            # Append to converted outputs
            converted_outputs[number] = percent

        # Check at least one panel is active
        active_panels = [panel for panel in self.panels if not panel.is_shutdown]
        self.num_active_panels = len(active_panels)
        if self.num_active_panels < 1:
            raise NoActivePanelsError(logger=self.logger)

        # Set outputs on each active panel
        active_panels = [panel for panel in self.panels if not panel.is_shutdown]
        for panel in active_panels:

            # Check if panel is active low
            if panel.active_low:
                self.logger.debug("panel is active low")
                converted_outputs_copy = converted_outputs.copy()
                for key in converted_outputs_copy.keys():
                    converted_outputs_copy[key] = 100 - converted_outputs_copy[key]

            # Set outputs on panel
            try:
                panel.driver.write_outputs(converted_outputs_copy)  # type: ignore
            except Exception as e:
                self.logger.exception("Unable to set output on `{}`".format(panel.name))
                panel.is_shutdown = True

        # Check at least one panel is still active
        active_panels = [panel for panel in self.panels if not panel.is_shutdown]
        self.num_active_panels = len(active_panels)
        if self.num_active_panels < 1:
            message = "failed when setting outputs"
            raise NoActivePanelsError(message=message, logger=self.logger)

    def set_output(self, channel_name: str, percent: float) -> None:
        """Sets output on each panel. Converts channel name to channel number 
        then sets output on dac."""
        self.logger.debug("Setting ch {}: {}".format(channel_name, percent))

        # Convert channel name to channel number
        try:
            channel_number = self.get_channel_number(channel_name)
        except Exception as e:
            raise SetOutputError(logger=self.logger) from e

        # Check at least one panel is active
        active_panels = [panel for panel in self.panels if not panel.is_shutdown]
        if len(active_panels) < 1:
            raise NoActivePanelsError(logger=self.logger)

        # Set output on each active panel
        active_panels = [panel for panel in self.panels if not panel.is_shutdown]
        for panel in active_panels:

            # Check if panel is active low
            if panel.active_low:
                percent = 100 - percent

            # Set output on panel
            try:
                panel.driver.write_output(channel_number, percent)  # type: ignore
            except Exception as e:
                self.logger.exception("Unable to set output on `{}`".format(panel.name))
                panel.is_shutdown = True

        # Check at least one panel is still active
        active_panels = [panel for panel in self.panels if not panel.is_shutdown]
        self.num_active_panels = len(active_panels)
        if self.num_active_panels < 1:
            message = "failed when setting output"
            raise NoActivePanelsError(message=message, logger=self.logger)

    def get_channel_number(self, channel_name: str) -> int:
        """Gets channel number from channel name."""
        for channel_config in self.channel_configs:
            if channel_config["name"]["brief"] == channel_name:  # type: ignore
                channel = channel_config["channel"]  # type: ignore
                channel_number = int(channel["software"])  # type: ignore
                return channel_number
        raise InvalidChannelNameError(message=channel_name, logger=self.logger)

    def build_channel_outputs(self, value: float) -> Dict[str, float]:
        """Build channel outputs. Sets each channel to provided value."""
        self.logger.debug("Building channel outputs")
        channel_outputs = {}
        for channel_config in self.channel_configs:
            name = channel_config["name"]["brief"]  # type: ignore
            channel_outputs[name] = value
        self.logger.debug("channel outputs = {}".format(channel_outputs))
        return channel_outputs
