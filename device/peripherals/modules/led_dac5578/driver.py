# Import standard python modules
import time

# Import python types
from typing import NamedTuple, Optional, Tuple, Dict, Any

# Import device utilities
from device.utilities.logger import Logger

# Import mux simulator
from device.comms.i2c2.mux_simulator import MuxSimulator

# Import dac driver elements
from device.peripherals.common.dac5578.driver import DAC5578Driver

# Import exceptions
from device.peripherals.classes.peripheral.exceptions import (
    DriverError,
    InitError,
    SetupError,
)


class LEDDAC5578Panel(object):
    """An led panel controlled by a dac5578."""

    # Initialize var defaults
    is_shutdown: bool = False
    driver: Optional[DAC5578Driver] = None

    def __init__(
        self,
        driver_name: str,
        config: Dict[str, Any],
        simulate: bool,
        mux_simulator: Optional[MuxSimulator],
    ) -> None:
        """Initializes panel."""

        # Initialize panel parameters
        self.driver_name = driver_name
        self.name = config.get("name")
        self.full_name = driver_name + "-" + self.name
        self.bus = config.get("bus")
        self.address = config.get("address")
        self.active_low = config.get("active_low")
        self.simulate = simulate
        self.mux_simulator = mux_simulator

        # Initialize i2c mux address
        self.mux = config.get("mux")
        if self.mux != None:
            self.mux = int(self.mux, 16)

        # Initialize i2c channel value
        self.channel = config.get("channel")
        if self.channel != None:
            self.channel = int(self.channel)

    def initialize(self) -> None:
        """Initializes panel."""
        try:
            self.driver = DAC5578Driver(
                name=self.full_name,
                bus=self.bus,
                address=self.address,
                mux=self.mux,
                channel=self.channel,
                simulate=self.simulate,
                mux_simulator=self.mux_simulator,
            )
        except Exception as e:
            self.logger.warning("Unable to initialize `{}`".format(self.name))
            self.is_shutdown = True


class LEDDAC5578Driver:
    """Driver for array of led panels controlled by a dac5578."""

    def __init__(
        self,
        name: str,
        panel_configs: Dict[str, Any],
        channel_configs: Dict[str, Any],
        simulate: bool = False,
        mux_simulator: Optional[MuxSimulator] = None,
    ) -> None:
        """Initializes driver."""

        # Initialize logger
        self.logger = Logger(name="Driver({})".format(name), dunder_name=__name__)

        # Initialize panels
        self.panels = []
        for config in panel_configs:
            panel = LEDDAC5578Panel(name, config, simulate, mux_simulator)
            panel.initialize()
            self.panels.append(panel)

    def turn_on(self) -> None:
        """Turns on led."""
        self.logger.debug("Turning on")

        # Turn on all active panels
        active_panels = [panel for panel in self.panels if not panel.is_shutdown]
        for panel in active_panels:
            channel_outputs = self.build_channel_outputs(100)
            panel.driver.set_outputs(channel_outputs)

    def turn_off(self) -> None:
        """Turns off led."""
        self.logger.debug("Turning off")

        # Turn off all active panels
        active_panels = [panel for panel in self.panels if not panel.is_shutdown]
        for panel in active_panels:
            channel_outputs = self.build_channel_outputs(0)
            panel.driver.set_outputs(channel_outputs)

    def set_output(self, channel_name: str, percent: float) -> None:
        """Sets output on each panel. Converts channel name to channel number 
        then sets output on dac."""
        self.logger.debug("Setting ch {}: {}".format(channel_name, percent))

        # Convert channel name to channel number
        try:
            channel_number = self.get_channel_number(channel_name)
        except Exception as e:
            raise SetOutputError(logger=self.logger) from e

        # Set output on each active panel
        active_panels = [panel for panel in self.panels if not panel.is_shutdown]
        for panel in active_panels:

            # Check if panel is active low
            if panel.active_low:
                percent = 100 - percent

            # Set output on panel
            try:
                panel.driver.set_output(channel_number, percent)
            except Exception as e:
                self.logger.warning("Unable to set output on `{}`".format(panel.name))
                panel.is_shutdown = True

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

        # Set outputs on each active panel
        active_panels = [panel for panel in self.panels if not panel.is_shutdown]
        for panel in active_panels:

            # Check if panel is active low
            if panel.active_low:
                converted_outputs = converted_outputs.copy()
                for key in converted_outputs.keys():
                    converted_outputs[key] = 100 - converted_outputs[key]

            # Set outputs on panel
            try:
                panel.driver.write_outputs(converted_outputs)
            except Exception as e:
                self.logger.warning("Unable to set output on `{}`".format(panel.name))
                panel.is_shutdown = True

    def get_channel_number(self, channel_name: str) -> int:
        """Gets channel number from channel name."""
        for channel_config in self.channel_configs:
            if channel_config["name"]["brief"] == channel_name:
                channel_number = int(channel_config["channel"]["software"])
                return channel_number
        raise InvalidChannelName(message=channel_name, logger=self.logger)
