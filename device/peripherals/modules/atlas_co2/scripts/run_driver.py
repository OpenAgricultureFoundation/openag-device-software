# Import standard python libraries
import os, sys, logging

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import typing modules
from typing import Any

# Import device utilities
from device.utilities.accessors import get_peripheral_config

# Import driver modules
from device.peripherals.classes.atlas.scripts.run_driver import (
    DriverRunner as AtlasDriverRunner,
)
from device.peripherals.modules.atlas_co2.driver import AtlasCo2Driver


class DriverRunner(AtlasDriverRunner):
    """Runs driver."""

    # Initialize driver class
    Driver = AtlasCo2Driver

    # Initialize defaults
    default_device = "atlas-co2"
    default_name = "AtlasCo2-Top"

    def __init__(self, *args: Any, **kwargs: Any):
        """Initializes run driver."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize parser
        self.parser.add_argument("--co2", action="store_true", help="read co2")
        self.parser.add_argument(
            "--enable-temp", action="store_true", help="enables internal temperature"
        )
        self.parser.add_argument(
            "--disable-temp", action="store_true", help="disable internal temperature"
        )
        self.parser.add_argument(
            "--temp", action="store_true", help="read internal temperature"
        )

    def run(self, *args: Any, **kwargs: Any):
        """Runs driver."""

        # Run parent class
        super().run(*args, **kwargs)

        # Check if reading pH
        if self.args.co2:
            print("CO2: {} ppm".format(self.driver.read_co2()))
        elif self.args.enable_temp:
            self.driver.enable_internal_temperature()
        elif self.args.disable_temp:
            self.driver.disable_internal_temperature()
        elif self.args.temp:
            print("Internal Temp: {} C".format(self.driver.read_internal_temperature()))


# Run main
if __name__ == "__main__":
    dr = DriverRunner()
    dr.run()
