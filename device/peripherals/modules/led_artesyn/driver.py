# Import standard python modules
import os, time, threading

# Import python types
from typing import NamedTuple, Optional, Tuple, Dict, Any, List

# Import device utilities
from device.utilities import logger, bitwise, maths

# Import peripheral utilities
from device.peripherals.utilities import light

# Import driver elements
from device.peripherals.modules.led_artesyn import exceptions

""" Notes from docs/iHP Communications Protocol  Definitions (Rev0.1).pdf

p.65 reading DIRECT data:
    Module PMBUS Command 8Bh (READ_VOUT)
    number of bytes = 3 
    Multiplier = N = 10000
    Command returns data of 0757B0h Converted to decimal = 481200
    Y = X * N 
    481200 = X * 10000
    X = 48.12 V

UDP packet format:

bytes of a COMMAND message: p.5
1-4     4 bytes message ID (I generate a sequential one).
  5     A1h (constant, except for ping which is A0h).
  6     000 + (low 5 bits internal device address) 00h=COMMS, mod1-8=10h-17h
  7     READ 01 + (low 6 bits for data length starting at 9th byte)
        WRITE 00 + (low 6 bits for data length starting at 9th byte)
  8     1 byte command code:  
            p.27 for module, p.44 for data sizes.
            p 47 for isocomm (all modules?), p.60 data sizes.
  9     Zero to N data bytes.

bytes of a RESPONSE message:  p.7
1-4     4 bytes message ID (matches what is sent in command)
  5     -0-- first nibble success
        -1-- first nibble error
        ---1 second nibble, message has response
        ---0 second nibble, message is blank
  6     0000 ---- normal, or error code in first nibble
  7     ---X XXXX device address
  8     --LL LLLL resonse data len
  9     1 byte command code
10+     response data bytes

EVERY message sent will be responded to (if valid and to active device).

#debugrob: also put a PING message in the config file.


p.20 error codes.
"""


class ArtesynDriver:
    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        simulate: bool,
        artesyn_config_file: str = None,
        debug: bool = False,
        logger: logger.Logger
    ) -> None:
        self.name = name
        self.simulate = simulate
        self.config_file = os.path.dirname(__file__) + '/' + artesyn_config_file
        self.debug = debug
        self.logger = logger

        # load our artesyn message config
        self.config = json.load(open(self.config_file, 'r'))
        self.logger.debug(f"loaded {self.config.get('name')}")
#debugrob: above for messages
# use bytes.fromhex() on the strings in the config file

    def write_outputs(outputs: Dict[int, float]) -> None:
        pass

    def write_output(channel_number: int, par_setpoint: float) -> None:
        pass


class LEDArtesynPanel:
    """An led panel controlled by a artesyn."""

    # Initialize var defaults
    is_shutdown: bool = True
    driver: Optional[ArtesynDriver] = None

    def __init__(
        self,
        driver_name: str,
        config: Dict[str, Any],
        simulate: bool,
        artesyn_config_file: str = None,
        debug: bool = False,
        logger: logger.Logger,
    ) -> None:
        """Initializes panel."""

        # Initialize panel parameters
        self.driver_name = driver_name
        self.name = str(config.get("name"))
        self.full_name = driver_name + "-" + self.name
        self.simulate = simulate
        self.artesyn_config_file = artesyn_config_file
        self.debug = debug
        self.logger = logger

    def initialize(self) -> None:
        """Initializes panel."""
        self.logger.debug("Initializing {}".format(self.name))
        try:
            self.driver = ArtesynDriver(
                name=self.full_name,
                simulate=self.simulate,
                artesyn_config_file=self.artesyn_config_file,
                debug=self.debug,
                logger=logger
            )
            self.is_shutdown = False
        except Exception as e:
            self.logger.exception("Unable to initialize `{}`".format(self.name))
            self.is_shutdown = True


class LEDArtesynDriver:
    """Driver for array of led panels controlled by a artesyn."""

    # Initialize var defaults
    num_active_panels = 0
    num_expected_panels = 1

    def __init__(
        self,
        name: str,
        panel_configs: List[Dict[str, Any]],
        panel_properties: Dict[str, Any],
        artesyn_config_file: str = None,
        debug: bool = False,
        simulate: bool = False
    ) -> None:
        """Initializes driver."""

        # Initialize driver parameters
        self.panel_properties = panel_properties
        self.simulate = simulate

        # Initialize logger
        logname = "Driver({})".format(name)
        self.logger = logger.Logger(logname, "peripherals")

#debugrob: fix here down


        # Initialze num expected panels
        self.num_expected_panels = len(panel_configs)

        # Initialize panels
        self.panels: List[LEDArtesynPanel] = []
        for config in panel_configs:
            panel = LEDArtesynPanel(
                    name, config, simulate, 
        artesyn_config_file: str = None,
        debug: bool = False,
                    self.logger)
            panel.initialize()
            self.panels.append(panel)

        # Check at least one panel is still active
        active_panels = [panel for panel in self.panels if not panel.is_shutdown]
        self.num_active_panels = len(active_panels)
        if self.num_active_panels < 1:
            raise exceptions.NoActivePanelsError(logger=self.logger)

        # Successfully initialized
        message = "Successfully initialized with {} ".format(self.num_active_panels)
        message2 = "active panels, expected {}".format(self.num_expected_panels)
        self.logger.debug(message + message2)

    def turn_on(self) -> Dict[str, float]:
        """Turns on leds."""
        self.logger.debug("Turning on")
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
            raise exceptions.SetSPDError(message=message, logger=self.logger) from e

        # Set outputs
        self.set_outputs(channel_outputs)

        # Successfully set channel outputs
        message = "Successfully set spd, output: channels={}, spectrum={}, intensity={}umol/m2/s".format(
            channel_outputs, output_spectrum, output_intensity
        )
        self.logger.debug(message)
        return channel_outputs, output_spectrum, output_intensity  # type: ignore

    def set_outputs(self, par_setpoints: dict) -> None:
        """Sets outputs on light panels. Converts channel names to channel numbers, 
        translates par setpoints to dac setpoints, then sets dac."""
        self.logger.debug("Setting outputs: {}".format(par_setpoints))

        # Check at least one panel is active
        active_panels = [panel for panel in self.panels if not panel.is_shutdown]
        self.num_active_panels = len(active_panels)
        if self.num_active_panels < 1:
            raise exceptions.NoActivePanelsError(logger=self.logger)
        message = "Setting outputs on {} active panels".format(self.num_active_panels)
        self.logger.debug(message)

        # Convert channel names to channel numbers
        converted_outputs = {}
        for name, percent in par_setpoints.items():

            # Convert channel name to channel number
            try:
                number = self.get_channel_number(name)
            except Exception as e:
                raise exceptions.SetOutputsError(logger=self.logger) from e

            # Append to converted outputs
            converted_outputs[number] = percent

        # Try to set outputs on all panels
        for panel in self.panels:

            # Set outputs on panel
            try:
                panel.driver.write_outputs(converted_outputs)  # type: ignore
            except AttributeError:
                message = "Unable to set outputs on `{}`".format(panel.name)
                self.logger.error(message + ", panel not initialized")
            except Exception as e:
                message = "Unable to set outputs on `{}`".format(panel.name)
                self.logger.exception(message)
                panel.is_shutdown = True

                # TODO: Check for new events in manager
                # Manager event functions can get called any time
                # As a special case, use function to set a new_event flag in driver
                # Check it here and break if panel failed
                # Only on panel failures b/c only ultra case leading to high latency..
                # at 5 seconds per failed panel (due to retry)
                # In a grid like SMHC, 25 panels * 5 seconds is grueling...
                # How to clear flag?...event handler process funcs all remove it

        # Check at least one panel is still active
        active_panels = [panel for panel in self.panels if not panel.is_shutdown]
        self.num_active_panels = len(active_panels)
        if self.num_active_panels < 1:
            message = "failed when setting outputs"
            raise exceptions.NoActivePanelsError(message=message, logger=self.logger)

    def set_output(self, channel_name: str, par_setpoint: float) -> None:
        """Sets output on light panels. Converts channel name to channel number, 
        translates par setpoint to dac setpoint, then sets dac."""
        self.logger.debug("Setting ch {}: {}".format(channel_name, par_setpoint))

        # Check at least one panel is active
        active_panels = [panel for panel in self.panels if not panel.is_shutdown]
        if len(active_panels) < 1:
            raise exceptions.NoActivePanelsError(logger=self.logger)
        message = "Setting output on {} active panels".format(self.num_active_panels)
        self.logger.debug(message)

        # Convert channel name to channel number
        try:
            channel_number = self.get_channel_number(channel_name)
        except Exception as e:
            raise exceptions.SetOutputError(logger=self.logger) from e

        # Set output on all panels
        for panel in self.panels:

            # Set output on panel
            try:
                panel.driver.write_output(channel_number, par_setpoint)  # type: ignore
            except AttributeError:
                message = "Unable to set output on `{}`".format(panel.name)
                self.logger.error(message + ", panel not initialized")
            except Exception as e:
                message = "Unable to set output on `{}`".format(panel.name)
                self.logger.exception(message)
                panel.is_shutdown = True

        # Check at least one panel is still active
        active_panels = [panel for panel in self.panels if not panel.is_shutdown]
        self.num_active_panels = len(active_panels)
        if self.num_active_panels < 1:
            message = "failed when setting output"
            raise exceptions.NoActivePanelsError(message=message, logger=self.logger)

    def get_channel_number(self, channel_name: str) -> int:
        """Gets channel number from channel name."""
        try:
            channel_dict = self.channels[channel_name]  # type: ignore
            channel_number = channel_dict.get("port", -1)
            return int(channel_number)
        except KeyError:
            raise exceptions.InvalidChannelNameError(
                message=channel_name, logger=self.logger
            )

    def build_channel_outputs(self, value: float) -> Dict[str, float]:
        """Build channel outputs. Sets each channel to provided value."""
        self.logger.debug("Building channel outputs")
        channel_outputs = {}
        for key in self.channels.keys():  # type: ignore
            channel_outputs[key] = value
        self.logger.debug("channel outputs = {}".format(channel_outputs))
        return channel_outputs

