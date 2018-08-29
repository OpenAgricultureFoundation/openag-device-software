# Import standard python modules
import time

# Import python types
from typing import Optional, Tuple, Dict

# Import device utilities
from device.utilities.logger import Logger

# Import peripheral utilities
from device.peripherals.utilities import light

# Import device drivers
from device.peripherals.common.driver.dac5578 import DAC5578Driver


class LEDDAC5578Panel:
    """An led panel controlled by a dac5578."""

    # Initialize shutdown state
    is_shutdown: bool = False

    def __init__(
        self,
        name: str,
        channel_configs: Dict[str, Any],
        bus: int,
        address: int,
        mux: Optional[int] = None,
        channel: Optional[int] = None,
        simulate: bool = False,
        active_low: bool = False,
    ):
        """Initializes panel."""

        # Initialize logger
        self.logger = Logger(name="Panel({})".format(name), dunder_name=__name__)

        # Initialize parameters
        self.name = name
        self.bus = bus
        self.addres = address
        self.mux = mux
        self.channel = channel
        self.channel_configs = channel_configs
        self.active_low = active_low

    def initialize(self) -> None:
        """Initializes panel."""
        self.logger.debug("Initializing panel")

        # Initialize driver
        try:
            self.driver = DAC5578Driver(
                name=name,
                bus=bus,
                address=address,
                mux=mux,
                channel=channel,
                simulate=simulate,
            )
        except DriverError as e:
            raise InitError(logger=self.logger) from e

    def reset(self):
        """Resets panel."""
        self.logger.debug("Resetting")
        self.is_shutdown = False

    def shutdown(self):
        """ Shutdown panel. """
        self.logger.debug("Shutting down")
        self.is_shutdown = True

    def set_output(self, channel_name: str, percent: float) -> None:
        """Sets output on dac. Converts channel name to channel number 
        then sets output on dac."""
        self.logger.debug("Setting ch {}: {}".format(channel_name, percent))

        # Check panel is not shutdown
        if self.is_shutdown:
            raise SetOutputError(message="panel is shutdown", logger=self.logger)

        # Convert channel name to channel number
        try:
            channel_number = self.get_channel_number(channel_name)
        except Exception as e:
            raise SetOutputError(logger=self.logger) from e

        # Check if panel is active low
        if self.active_low:
            percent = 100 - percent

        # Write output to dac
        try:
            self.driver.write_output(channel_number, percent)
        except DriverError as e:
            raise SetOutputError(logger=self.logger) from e

    def set_outputs(self, outputs: dict) -> None:
        """Sets outputs on dac. Converts channel names to channel numbers 
        then sets outputs on dac."""
        self.logger.debug("Setting outputs: {}".format(outputs))

        # Check panel is not shutdown
        if self.is_shutdown:
            raise SetOutputsError(message="panel is shutdown", logger=self.logger)

        # Convert channel names to channel numbers
        converted_outputs = {}
        for name, percent in outputs.items():

            # Convert channel name to channel number
            try:
                number = self.get_channel_number(name)
            except Exception as e:
                raise SetOutputsError(logger=self.logger) from e

            # Check for active low
            if self.active_low:
                percent = 100 - percent

            # Append to converted outputs
            converted_outputs[number] = percent

            # Write outputs to dac
            try:
                self.driver.write_outputs(converted_outputs)
            except DriverError as e:
                raise SetOutputsError(logger=self.logger) from e

    def set_spd(
        self,
        desired_distance_cm: float,
        desired_ppfd_umol_m2_s: float,
        desired_spectrum_nm_percent: dict,
    ) -> Tuple[Optional[dict], Optional[dict], Optional[dict]]:
        """Sets spectral power distribution."""
        self.logger.debug(
            "Setting spd, distance={}cm, ppfd={}umol/m2/s, spectrum={}".format(
                desired_distance_cm, desired_ppfd_umol_m2_s, desired_spectrum_nm_percent
            )
        )

        # Check panel is not shutdown
        if self.is_shutdown:
            raise SetOutputsError(message="panel is shutdown", logger=self.logger)

        # Approximate spectral power distribution
        try:
            channel_outputs, output_spectrum_nm_percent, output_ppfd_umol_m2_s = light.approximate_spd(
                channel_configs=self.channel_configs,
                desired_distance_cm=desired_distance_cm,
                desired_ppfd_umol_m2_s=desired_ppfd_umol_m2_s,
                desired_spectrum_nm_percent=desired_spectrum_nm_percent,
            )
        except Exception as e:
            raise SetSPDError(logger=self.logger) from e

        # Set channel outputs
        try:
            self.set_outputs(channel_outputs)
        except Exception as e:
            raise SetSPDError(logger=self.logger) from e


        # Successfully set channel outputs
        self.logger.debug(
            "Successfully set spd, output: channels={}, spectrum={}, ppfd={}umol/m2/s".format(
                channel_outputs, output_spectrum_nm_percent, output_ppfd_umol_m2_s
            )
        )
        return (
            channel_outputs,
            output_spectrum_nm_percent,
            output_ppfd_umol_m2_s,
        )

    def turn_on(self) -> None:
        """Turns on all channels."""
        self.logger.debug("Turning on")

        # Check panel is not shutdown
        if self.is_shutdown:
            raise PanelShutdownError(logger=self.logger)

        # Set channels to 100%
        try:
            channel_outputs = self.build_channel_outputs(100)
            self.set_outputs(channel_outputs)
        except Exception as e:
            raise TurnOnError(logger=self.logger) from e

    def turn_off(self) -> None:
        """Turns off all channels."""
        self.logger.debug("Turning off")

        # Check panel is not shutdown
        if self.is_shutdown:
            raise PanelShutdownError(logger=self.logger)

        # Set channels to 0%
        try:
            channel_outputs = self.build_channel_outputs(0)
            self.set_outputs(channel_outputs)
        except Exception as e:
            raise TurnOffError(logger=self.logger) from e

    def fade(self, cycles: int) -> None:
        """ Fades channels sequentially"""
        self.logger.debug("Fading")

        # Check panel is not shutdown
        if self.is_shutdown:
            raise PanelShutdownError(logger=self.logger)
        
        # Fade panel
        try:

            # Turn off panel
            self.turn_off()

            # Get channel names from outputs
            channel_outputs = self.build_channel_outputs(0)
            channel_names = channel_outputs.keys()

        # Repeat for number of specified cycles
        for i in range(cycles):

            # Cycle through channels
            for channel_name in channel_names:

                # Fade up
                for value in range(0, 100, 10):
                    self.logger.info("Channel {}: {}%".format(channel_name, value))
                    try:
                        self.set_output(channel_name, value)
                    except Exception as e:
                        raise FadeError(logger=self.logger) from e
                    time.sleep(0.1)

                # Fade down
                for value in range(100, 0, -10):
                    self.logger.info("Channel {}: {}%".format(channel_name, value))
                    try:
                        self.set_output(channel_name, value)
                    except Exception as e:
                        raise FadeError(logger=self.logger) from e
                    time.sleep(0.1)


    def get_channel_number(self, channel_name: str) -> int:
        """Gets channel number from channel name."""
        for channel_config in self.channel_configs:
            if channel_config["name"]["brief"] == channel_name:
                channel_number = int(channel_config["channel"]["software"])
                return channel_number
        raise InvalidChannelName(message=channel_name, logger=self.logger)

    def build_channel_outputs(self, value: float) -> Dict[str, float]:
        """Build channel outputs. Sets each channel to provided value."""
        channel_outputs = {}
        for channel_config in self.channel_configs:
            name = channel_config["name"]["brief"]
            channel_outputs[name] = value
        return channel_outputs
