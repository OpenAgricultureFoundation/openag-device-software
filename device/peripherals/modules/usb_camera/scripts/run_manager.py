# Import standard python libraries
import os, sys

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import run peripheral parent class
from device.peripherals.classes.peripheral.scripts.run_manager import ManagerRunnerBase

# Import peripheral manager
from device.peripherals.modules.usb_camera.manager import USBCameraManager


class ManagerRunner(ManagerRunnerBase):  # type: ignore
    """Runs manager."""

    # Initialize manager class
    Manager = USBCameraManager

    # Initialize defaults
    default_device = "edu-v0.1.0"
    default_name = "Camera-Top"


# Run main
if __name__ == "__main__":
    runner = ManagerRunner()
    runner.run()
