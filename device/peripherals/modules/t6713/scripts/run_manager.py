# Import standard python libraries
import os, sys

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import run peripheral parent class
from device.peripherals.classes.peripheral.scripts.run_manager import ManagerRunnerBase

# Import peripheral manager
from device.peripherals.modules.t6713.manager import T6713Manager


class ManagerRunner(ManagerRunnerBase):  # type: ignore
    """Runs manager."""

    # Initialize manager class
    Manager = T6713Manager

    # Initialize defaults
    default_device = "edu-v0.1.0"
    default_name = "T6713-Top"


# Run main
if __name__ == "__main__":
    runner = ManagerRunner()
    runner.run()
