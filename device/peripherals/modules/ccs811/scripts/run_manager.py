# Import standard python libraries
import os, sys

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import run peripheral parent class
from device.peripherals.classes.peripheral.scripts.run_manager import ManagerRunnerBase

# Import peripheral manager
from device.peripherals.modules.ccs811.manager import CCS811Manager


class ManagerRunner(ManagerRunnerBase):  # type: ignore
    """Runs manager."""

    # Initialize manager class
    Manager = CCS811Manager

    # Initialize defaults
    default_device = "edu-v0.2.0"
    default_name = "CCS811-Top"


# Run main
if __name__ == "__main__":
    runner = ManagerRunner()
    runner.run()
