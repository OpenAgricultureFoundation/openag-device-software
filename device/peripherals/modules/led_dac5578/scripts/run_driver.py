# Import standard python modules
import os, sys, threading

# Import python types
from typing import Any

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import run peripheral parent class
from device.peripherals.classes.peripheral.scripts.run_peripheral import RunnerBase

# Import driver
from device.peripherals.modules.led_dac5578.driver import LEDDAC5578Driver


class DriverRunner(RunnerBase):  # type: ignore
    """Runs driver."""

    # Initialize defaults
    default_device = "edu-v0.1.0"
    default_name = "LEDPanel-Top"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes run driver."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize parser
        self.parser.add_argument("--on", action="store_true", help="turn on leds")
        self.parser.add_argument("--off", action="store_true", help="turn off leds")
        self.parser.add_argument("--set-spd", action="store_true", help="sets spd")
        self.parser.add_argument(
            "--channel", type=int, help="set channel name (e.g. CW"
        )
        self.parser.add_argument("--percent", type=int, help="set output (0-100)")

    def run(self, *args: Any, **kwargs: Any) -> None:
        """Runs driver."""

        # Run parent class
        super().run(*args, **kwargs)

        # Initialize panel variables
        self.panel_configs = self.communication.get("panels")
        self.panel_properties = self.peripheral_setup.get("properties")

        # Initialize driver
        self.driver = LEDDAC5578Driver(
            name=self.args.name,
            i2c_lock=threading.RLock(),
            panel_configs=self.panel_configs,
            panel_properties=self.panel_properties,
        )

        # Check if setting a channel to a value
        if self.args.channel != None and self.args.percent != None:
            self.driver.set_output(self.args.channel, self.args.percent)

        # Check if setting all channels to a value
        elif self.args.channel == None and self.args.percent != None:
            channel_names = self.panel_properties.get("channels", {}).keys()
            channel_outputs = {}
            for channel_name in channel_names:
                channel_outputs[channel_name] = self.args.percent
            self.driver.set_outputs(channel_outputs)

        # Check if turning on
        elif self.args.on:
            self.driver.turn_on()

        # Check if turning off
        elif self.args.off:
            self.driver.turn_off()

        # Check if setting spd
        elif self.args.set_spd:

            distance = 10
            ppfd = 800
            spectrum = {
                "380-399": 0,
                "400-499": 26,
                "500-599": 22,
                "600-700": 39,
                "701-780": 13,
            }
            self.driver.set_spd(distance, ppfd, spectrum)


# Run main
if __name__ == "__main__":
    dr = DriverRunner()
    dr.run()
