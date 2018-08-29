# Import standard python modules
import os, sys

# Import python types
from typing import Any

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

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
        self.parser.add_argument("--fade", action="store_true", help="fade leds")

    def run(self, *args: Any, **kwargs: Any) -> None:
        """Runs driver."""

        # Run parent class
        super().run(*args, **kwargs)

        # Initialize driver
        self.driver = LEDDAC5578Driver(
            name=self.args.name,
            panel_configs=self.communication.get("panels"),
            channel_configs=self.peripheral_setup.get("channel_configs"),
        )

        # Check if turning on
        if self.args.on:
            self.driver.turn_on()

        # Check if turning off
        elif self.args.off:
            self.driver.turn_off()

        # Check if fading
        elif self.args.fade:
            self.driver.fade()


# Run main
if __name__ == "__main__":
    dr = DriverRunner()
    dr.run()
