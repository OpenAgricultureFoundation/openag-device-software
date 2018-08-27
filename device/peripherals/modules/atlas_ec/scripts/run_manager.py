# Import standard python libraries
import os, sys, logging

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import typing modules
from typing import Any

# Import run peripheral parent class
from device.peripherals.classes.peripheral.scripts.run_manager import ManagerRunnerBase

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.accessors import get_peripheral_config

# Import device state
from device.state import State

# Import peripheral manager
from device.peripherals.modules.atlas_ec.manager import AtlasECManager


class ManagerRunner(ManagerRunnerBase):
    """Runs manager."""

    # Initialize manager class
    Manager = AtlasECManager

    # Initialize defaults
    default_device = "edu-v0.1.0"
    default_name = "AtlasEC-Reservoir"

    def __init__(self, *args: Any, **kwargs: Any):
        """Initializes run driver."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize parser
        self.parser.add_argument(
            "--calibrate-dry", action="store_true", help="take dry calibration"
        )
        self.parser.add_argument(
            "--calibrate-low", type=float, help="take a low point calibration"
        )
        self.parser.add_argument(
            "--calibrate-high", type=float, help="take a high point calibration"
        )
        self.parser.add_argument(
            "--calibrate-single", type=float, help="take a single point calibration"
        )
        self.parser.add_argument(
            "--calibrate-clear", action="store_true", help="clears calibration readings"
        )

    def run(self, *args, **kwargs):
        """Runs driver."""

        # Run parent class
        super().run(*args, **kwargs)

        # Check taking dry point calibration reading
        if self.args.calibrate_dry:
            self.manager.mode = Modes.CALIBRATE
            request_type = "Dry Calibration"
            request = {"type": request_type}
            self.manager.process_event(request)
            print(self.manager.response["message"])

        # Check if taking low point calibration reading
        elif self.args.calibrate_low:
            self.manager.mode = Modes.CALIBRATE
            request_type = "Low Point Calibration"
            request = {"type": request_type, "value": self.args.calibrate_low}
            self.manager.process_event(request)
            print(self.manager.response["message"])

        # Check if taking high point calibration reading
        elif self.args.calibrate_high:
            self.manager.mode = Modes.CALIBRATE
            request_type = "High Point Calibration"
            request = {"type": request_type, "value": self.args.calibrate_high}
            self.manager.process_event(request)
            print(self.manager.response["message"])

        # Check taking single point calibration reading
        elif self.args.calibrate_single:
            self.manager.mode = Modes.CALIBRATE
            request_type = "Single Point Calibration"
            request = {"type": request_type, "value": self.args.calibrate_single}
            self.manager.process_event(request)
            print(self.manager.response["message"])

        # Check if clearing calibration readings
        elif self.args.calibrate_clear:
            self.manager.mode = Modes.CALIBRATE
            self.manager.process_event({"type": "Clear Calibration"})
            print(self.manager.response["message"])


# Run main
if __name__ == "__main__":
    runner = ManagerRunner()
    runner.run()
