# Import standard python libraries
import os, sys

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import run peripheral parent class
from device.peripherals.classes.peripheral.scripts.run_manager import ManagerRunnerBase

# Import peripheral manager
from device.peripherals.modules.led_dac5578.manager import LEDDAC5578Manager


class ManagerRunner(ManagerRunnerBase):  # type: ignore
    """Runs manager."""

    # Initialize manager class
    Manager = LEDDAC5578Manager

    # Initialize defaults
    default_device = "edu-v0.1.0"
    default_name = "LEDPanel-Top"


# Run main
if __name__ == "__main__":
    runner = ManagerRunner()
    runner.run()
