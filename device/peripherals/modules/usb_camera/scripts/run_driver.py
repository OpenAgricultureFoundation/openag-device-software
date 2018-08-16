# Import standard python libraries
import os, sys

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import run peripheral parent class
from device.peripherals.classes.peripheral_runner import PeripheralRunner

# Import device utilities
from device.utilities.accessors import get_peripheral_config

# Import driver
from device.peripherals.modules.usb_camera.driver import USBCameraDriver


class DriverRunner(PeripheralRunner):
    """Runs driver."""

    def __init__(self, *args, **kwargs):
        """Initializes run driver."""
        super().__init__(*args, **kwargs)

        # Initialize parser
        self.parser.add_argument(
            "--capture", action="store_true", help="captures image, manages mux"
        )
        self.parser.add_argument(
            "--capture-image", action="store_true", help="captures image"
        )
        self.parser.add_argument(
            "--capture-dummy-image", action="store_true", help="captures dummy image"
        )

    def run(self, *args, **kwargs):
        """Runs driver."""
        super().run(*args, **kwargs)

        # Initialize directory
        root_dir = os.environ["OPENAG_BRAIN_ROOT"]
        directory = root_dir + "/device/peripherals/modules/usb_camera/scripts/images/"

        # Initialize driver
        self.driver = USBCameraDriver(
            name=self.args.name,
            vendor_id=int(self.peripheral_setup["properties"]["vendor_id"], 16),
            product_id=int(self.peripheral_setup["properties"]["product_id"], 16),
            resolution=self.peripheral_setup["properties"]["resolution"],
            directory=directory,
            usb_mux_comms=self.communication.get("usb_mux_comms", None),
            usb_mux_channel=self.communication.get("usb_mux_channel", None),
        )

        # Check if capturing image w/mux management
        if self.args.capture:
            print("Capturing image")
            error = self.driver.capture()
            if error.exists():
                print("Error: {}".format(error.trace))
            else:
                print("Successfully captured image!")

        # Check if capturing image
        elif self.args.capture_image:
            print("Capturing image")
            error = self.driver.capture_image()
            if error.exists():
                print("Error: {}".format(error.trace))
            else:
                print("Successfully captured image!")

        # Check if capturing dummy image
        elif self.args.capture_dummy_image:
            print("Capturing dummy image")
            error = self.driver.capture_dummy_image()
            if error.exists():
                print("Error: {}".format(error.trace))
            else:
                print("Successfully captured dummy image!")


# Run main
if __name__ == "__main__":
    dr = DriverRunner()
    dr.run()
