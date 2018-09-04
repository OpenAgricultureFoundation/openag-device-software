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
from device.peripherals.modules.atlas_do.manager import AtlasDOManager


class ManagerRunner(ManagerRunnerBase):
    """Runs manager."""

    # Initialize manager class
    Manager = AtlasDOManager

    # Initialize defaults
    default_device = "unspecified"  # TODO: build a config that uses a DO sensor
    default_name = "AtlasDO-Reservoir"


# Run main
if __name__ == "__main__":
    runner = ManagerRunner()
    runner.run()
