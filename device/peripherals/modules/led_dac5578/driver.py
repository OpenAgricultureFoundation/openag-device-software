# Import standard python modules
import time, threading

# Import python types
from typing import NamedTuple, Optional, Tuple, Dict, Any, List

# Import device utilities
from device.utilities.logger import Logger
from device.utilities import maths

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
        panel_properties: Dict[str, Any],
        i2c_lock: threading.Lock,
        simulate: bool = False,
        mux_simulator: Optional[MuxSimulator] = None,
    ) -> None:
        """Initializes driver."""

        # Initialize driver parameters
        self.panel_properties = panel_properties
        self.i2c_lock = i2c_lock
        self.simulate = simulate

        # Initialize logger
        self.logger = Logger(name="Driver({})".format(name), dunder_name=__name__)

        # Parse panel properties
        self.channels = self.panel_properties.get("channels")
        self.logic_map = self.panel_properties.get("logic_scaler_percents")

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
        self, desired_distance: float, desired_intensity: float, desired_spectrum: Dict
    ) -> Tuple[Optional[Dict], Optional[Dict], Optional[Dict]]:
        """Sets spectral power distribution."""
        message = "Setting spd, distance={}cm, ppfd={}umol/m2/s, spectrum={}".format(
            desired_distance, desired_intensity, desired_spectrum
        )
        self.logger.debug(message)

        # Approximate spectral power distribution
        try:
            channel_outputs, output_spectrum, output_intensity = light.approximate_spd(
                self.panel_properties,
                desired_distance,
                desired_intensity,
                desired_spectrum,
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
                self.logger.exception("Unable to set outputs on {}".format(panel.name))

        # Check at least one panel is still active
        active_panels = [panel for panel in self.panels if not panel.is_shutdown]
        if len(active_panels) < 1:
            message = "failed when setting spd"
            raise NoActivePanelsError(message=message, logger=self.logger)

        # Successfully set channel outputs
        self.logger.debug(
            "Successfully set spd, output: channels={}, spectrum={}, ppfd={}umol/m2/s".format(
                channel_outputs, output_spectrum, output_intensity
            )
        )
        return (channel_outputs, output_spectrum, output_intensity)

    def set_outputs(self, outputs: dict) -> None:
        """Sets outputs on dac. Converts channel names to channel numbers 
        then sets outputs on dac."""
        self.logger.debug("Setting outputs: {}".format(outputs))

        # Check at least one panel is active
        active_panels = [panel for panel in self.panels if not panel.is_shutdown]
        self.num_active_panels = len(active_panels)
        if self.num_active_panels < 1:
            raise NoActivePanelsError(logger=self.logger)
        self.logger.debug(
            "Setting outputs on {} active panels".format(self.num_active_panels)
        )

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

        # Set outputs on each active panel
        # active_panels = [panel for panel in self.panels if not panel.is_shutdown]
        # for panel in active_panels:

        # TODO: Change this back to only active panels

        # Try to set outputs on all panels
        for panel in self.panels:

            # Scale setpoints
            scaled_outputs = self.scale_outputs(converted_outputs)

            # Adjust logic ouput by checking if panel is active low
            if panel.active_low:
                logic_outputs = scaled_outputs.copy()
                for key in logic_outputs.keys():
                    logic_outputs[key] = 100 - logic_outputs[key]
            else:
                logic_outputs = scaled_outputs

            # Set outputs on panel
            try:
                panel.driver.write_outputs(logic_outputs)  # type: ignore
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

        # Check at least one panel is active
        active_panels = [panel for panel in self.panels if not panel.is_shutdown]
        if len(active_panels) < 1:
            raise NoActivePanelsError(logger=self.logger)
        self.logger.debug(
            "Setting output on {} active panels".format(self.num_active_panels)
        )

        # Convert channel name to channel number
        try:
            channel_number = self.get_channel_number(channel_name)
        except Exception as e:
            raise SetOutputError(logger=self.logger) from e

        # Set output on each active panel
        # active_panels = [panel for panel in self.panels if not panel.is_shutdown]
        # for panel in active_panels:

        # TODO: Change this back to only active panels

        # Set output on all panels
        for panel in self.panels:

            # Scale setpoint
            percent = self.scale_output(percent)

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
        try:
            channel_dict = self.channels[channel_name]
            channel_number = channel_dict.get("port", -1)
            return int(channel_number)
        except KeyError:
            raise InvalidChannelNameError(message=channel_name, logger=self.logger)

    def build_channel_outputs(self, value: float) -> Dict[str, float]:
        """Build channel outputs. Sets each channel to provided value."""
        self.logger.debug("Building channel outputs")
        channel_outputs = {}
        for key in self.channels.keys():
            channel_outputs[key] = value
        self.logger.debug("channel outputs = {}".format(channel_outputs))
        return channel_outputs

    def scale_outputs(self, outputs: Dict) -> Dict:
        """Scales setpoint (light intensity %) to ouput logic (dac signal %)"""

        # Build interpolation lists
        logic_list = []
        setpoint_list = []
        for logic, setpoint in self.logic_map.items():
            logic_list.append(float(logic))
            setpoint_list.append(float(setpoint))

        # Get scaled setpoints
        scaled_outputs = {}
        for key, output in outputs.items():
            scaled_output = maths.interpolate(setpoint_list, logic_list, output)
            scaled_outputs[key] = scaled_output

        # Successfully scaled outputs
        return scaled_outputs

    def scale_output(self, output: float) -> float:
        """Scales setpoint (light intensity %) to ouput logic (dac signal %)"""

        # Build interpolation lists
        logic_list = []
        setpoint_list = []
        for logic, setpoint in self.logic_map.items():
            logic_list.append(float(logic))
            setpoint_list.append(float(setpoint))

        # Build channel setpoint list
        scaled_output = maths.interpolate(setpoint_list, logic_list, output)

        # Successfully built channel setpoint list
        return scaled_output
