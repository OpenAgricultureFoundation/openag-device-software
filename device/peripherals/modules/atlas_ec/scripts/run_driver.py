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
from device.peripherals.modules.atlas_ec.driver import AtlasECDriver

# Ensure virtual environment is activated
if os.getenv("VIRTUAL_ENV") == None:
    print("Please activate your virtual environment then re-run script")
    exit(0)

# Ensure platform info is sourced
if os.getenv("PLATFORM") == None:
    print("Please source your platform info then re-run script")
    exit(0)


class DriverRunner(AtlasDriverRunner):
    """Runs driver."""

    # Initialize driver class
    Driver = AtlasECDriver

    # Initialize defaults
    default_device = "edu-v0.1.0"
    default_name = "AtlasEC-Reservoir"

    def __init__(self, *args: Any, **kwargs: Any):
        """Initializes run driver."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize parser
        self.parser.add_argument("--ec", action="store_true", help="read EC")
        self.parser.add_argument(
            "--enable-ec", action="store_true", help="enable EC output"
        )
        self.parser.add_argument(
            "--disable-ec", action="store_true", help="disable EC output"
        )
        self.parser.add_argument(
            "--enable-tds", action="store_true", help="enable TDS output"
        )
        self.parser.add_argument(
            "--disable-tds", action="store_true", help="disable TDS output"
        )
        self.parser.add_argument(
            "--enable-salinity", action="store_true", help="enable salinity output"
        )
        self.parser.add_argument(
            "--disable-salinity", action="store_true", help="disable salinity output"
        )
        self.parser.add_argument(
            "--enable-sg", action="store_true", help="enable specific gravity output"
        )
        self.parser.add_argument(
            "--disable-sg", action="store_true", help="disable specific gravity output"
        )
        self.parser.add_argument("--set-probe", type=float, help="set probe type")
        self.parser.add_argument(
            "--calibrate-dry", action="store_true", help="take dry calibration"
        )
        self.parser.add_argument(
            "--calibrate-single", type=float, help="take single point calibration"
        )

    def run(self, *args: Any, **kwargs: Any):
        """Runs driver."""

        # Run parent class
        super().run(*args, **kwargs)

        # Check if reading pH
        if self.args.ec:
            print("EC: {}".format(self.driver.read_ec()))

        # Check if enabling ec output
        elif self.args.enable_ec:
            self.driver.enable_ec_output()

        # Check if disabling ec output
        elif self.args.disable_ec:
            self.driver.disable_ec_output()

        # Check if enabling ec output
        elif self.args.enable_tds:
            self.driver.enable_tds_output()

        # Check if disabling tds output
        elif self.args.disable_tds:
            self.driver.disable_tds_output()

        # Check if enabling salinity output
        elif self.args.enable_salinity:
            self.driver.enable_salinity_output()

        # Check if disabling salinity output
        elif self.args.disable_salinity:
            self.driver.disable_salinity_output()

        # Check if enabling specific gravity output
        elif self.args.enable_sg:
            self.driver.enable_specific_gravity_output()

        # Check if disabling specific gravity output
        elif self.args.disable_sg:
            self.driver.disable_specific_gravity_output()

        # Check if setting probe type
        elif self.args.set_probe:
            self.driver.set_probe_type(self.args.set_probe)

        # Check if calibrating dry
        elif self.args.calibrate_dry:
            self.driver.take_dry_calibration_reading()

        # Check if taking single point calibration reading
        elif self.args.calibrate_single:
            self.driver.take_single_point_calibration_reading(
                self.args.calibrate_single
            )


# Run main
if __name__ == "__main__":
    dr = DriverRunner()
    dr.run()
