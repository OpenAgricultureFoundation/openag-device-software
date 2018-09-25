# Import standard python libraries
import os, sys, logging

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import typing modules
from typing import Any

# Import device utilities
from device.utilities.modes import Modes

# Import run peripheral parent class
from device.peripherals.classes.peripheral.scripts.run_manager import ManagerRunnerBase

# Import peripheral manager
from device.peripherals.modules.atlas_temp.manager import AtlasTempManager


class ManagerRunner(ManagerRunnerBase):
    """Runs manager."""

    # Initialize manager class
    Manager = AtlasTempManager

    # Initialize defaults
    default_device = "edu-v0.3.0"
    default_name = "AtlasTemp-Reservoir"


# Run main
if __name__ == "__main__":
    runner = ManagerRunner()
    runner.run()
