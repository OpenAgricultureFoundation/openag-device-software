# Import standard python libraries
import os, sys, threading

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import run peripheral parent class
from device.peripherals.classes.peripheral.scripts.run_peripheral import RunnerBase

# Import driver
from device.peripherals.modules.usb_camera.driver import USBCameraDriver


class DriverRunner(RunnerBase):
    """Runs driver."""

    # Initialize defaults
    default_device = "edu-v0.1.0"
    default_name = "Camera-Top"

    def __init__(self, *args, **kwargs):
        """Initializes run driver."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize parser
        self.parser.add_argument(
            "--capture", action="store_true", help="captures image, manages mux"
        )
        self.parser.add_argument(
            "--capture-image", action="store_true", help="captures image"
        )

    def run(self, *args, **kwargs):
        """Runs driver."""

        # Run parent class
        super().run(*args, **kwargs)

        # Initialize driver
        self.driver = USBCameraDriver(
            name=self.args.name,
            vendor_id=int(self.peripheral_setup["properties"]["vendor_id"], 16),
            product_id=int(self.peripheral_setup["properties"]["product_id"], 16),
            resolution=self.peripheral_setup["properties"]["resolution"],
            usb_mux_comms=self.communication.get("usb_mux_comms", None),
            usb_mux_channel=self.communication.get("usb_mux_channel", None),
            i2c_lock=threading.RLock(),
        )

        # Check if capturing image w/mux management
        if self.args.capture:
            self.driver.capture()

        # Check if capturing image
        elif self.args.capture_image:
            self.driver.capture_image()


# Run main
if __name__ == "__main__":
    dr = DriverRunner()
    dr.run()
