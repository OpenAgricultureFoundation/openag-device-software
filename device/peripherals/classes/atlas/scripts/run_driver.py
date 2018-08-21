# Import standard python libraries
import os, sys

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import type checks
from typing import Any

# Import run peripheral parent class
from device.peripherals.classes.peripheral_runner import PeripheralRunner

# Import device utilities
from device.utilities.accessors import get_peripheral_config

# Import driver
from device.peripherals.classes.atlas.driver import AtlasDriver


class DriverRunner(PeripheralRunner):  # type: ignore
    """Runs driver."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes run driver."""
        super().__init__(*args, **kwargs)

        # Initialize parser
        self.parser.add_argument("--info", action="store_true", help="read info")
        self.parser.add_argument("--status", action="store_true", help="read status")
        self.parser.add_argument(
            "--enable-plock", action="store_true", help="enables protocol lock"
        )
        self.parser.add_argument(
            "--disable-plock", action="store_true", help="disables protocol lock"
        )
        self.parser.add_argument(
            "--enable-led", action="store_true", help="enables led"
        )
        self.parser.add_argument(
            "--disable-led", action="store_true", help="disables led"
        )

        self.parser.add_argument(
            "--sleep", action="store_true", help="enable sleep mode"
        )

    def initialize_driver(self):
        """Initialzes driver instance."""

        # Initialize driver optional parameters
        mux = self.communication.get("mux", None)
        if mux != None:
            mux = int(mux, 16)

        # Initialize driver
        self.driver = AtlasDriver(
            name=self.args.name,
            bus=self.communication["bus"],
            address=int(self.communication["address"], 16),
            mux=mux,
            channel=self.communication.get("channel", None),
        )

    def run(self, *args: Any, **kwargs: Any) -> None:
        """Runs driver."""
        super().run(*args, **kwargs)

        # Initialize driver
        self.initialize_driver()

        # Check if reading info
        if self.args.info:
            print("Reading info")
            info = self.driver.read_info()
            print(info)

        # Check if reading status
        elif self.args.status:
            print("Reading status")
            status = self.driver.read_status()
            print(status)

        # Check if enabling protocol lock
        elif self.args.enable_plock:
            print("Enabling protocol lock")
            self.driver.enable_protocol_lock()

        # Check if disabling protocol lock
        elif self.args.disable_plock:
            print("Disabling protocol lock")
            self.driver.disable_protocol_lock()

        # Check if enabling led
        elif self.args.enable_led:
            print("Enabling LED")
            self.driver.enable_led()

        # Check if disabling led
        elif self.args.disable_led:
            print("Disabling LED")
            self.driver.disable_led()

        # Check if reading status
        elif self.args.sleep:
            print("Enabling sleep mode")
            self.driver.enable_sleep_mode()


# Run main
if __name__ == "__main__":
    dr = DriverRunner()
    dr.run()
