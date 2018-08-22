# Import standard python libraries
import os, sys, logging

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import typing modules
from typing import Any

# Import device utilities
from device.utilities.accessors import get_peripheral_config

# Import driver modules
from device.peripherals.classes.atlas.scripts.run_driver import DriverRunner as AtlasDriverRunner
from device.peripherals.modules.atlas_ph.driver import AtlasPHDriver


class DriverRunner(AtlasDriverRunner):
    """Runs driver."""

    # Initialize driver class
    Driver = AtlasPHDriver

    # Initialize defaults
    default_device = "edu-v0.1.0"
    default_name = "AtlasPH-Reservoir"

    def __init__(self, *args: Any, **kwargs: Any):
        """Initializes run driver."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize parser
        self.parser.add_argument("--ph", action="store_true", help="read pH")
        self.parser.add_argument(
            "--set-temp", type=float, help="set compensation temperature in Celcius"
        )
        self.parser.add_argument(
            "--calibrate-low", type=float, help="take low point calibration reading"
        )
        self.parser.add_argument(
            "--calibrate-mid", type=float, help="take mid point calibration reading"
        )
        self.parser.add_argument(
            "--calibrate-high", type=float, help="take high point calibration reading"
        )
        self.parser.add_argument(
            "--calibrate-clear", action="store_true", help="clear calibration readings"
        )

    def run(self, *args: Any, **kwargs: Any):
        """Runs driver."""

        # Run parent class
        super().run(*args, **kwargs)

        # Check if reading pH
        if self.args.ph:
            print("pH: {}".format(self.driver.read_ph()))

        # Check if setting compensation temperature
        elif self.args.set_temp:
            self.driver.set_compensation_temperature(float(self.args.set_temp))

        # Check if taking low point calibration
        elif self.args.calibrate_low:
            self.driver.take_low_point_calibration_reading(
                float(self.args.calibrate_low)
            )

        # Check if taking mid point calibration
        elif self.args.calibrate_mid:
            self.driver.take_mid_point_calibration_reading(
                float(self.args.calibrate_mid)
            )

        # Check if taking low point calibration
        elif self.args.calibrate_high:
            self.driver.take_high_point_calibration_reading(
                float(self.args.calibrate_high)
            )

        # Check if clearing calibration
        elif self.args.calibrate_clear:
            self.driver.clear_calibration_readings()


# Run main
if __name__ == "__main__":
    dr = DriverRunner()
    dr.run()
