# Import standard python libraries
import os, sys

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import type checks
from typing import Any

# Import run peripheral parent class
from device.peripherals.classes.peripheral.runner import RunnerBase

# Import device utilities
from device.utilities.accessors import get_peripheral_config

# Import driver
from device.peripherals.classes.atlas.driver import AtlasDriver


class DriverRunner(RunnerBase):  # type: ignore
    """Runs driver."""

    # Initialize driver class
    Driver = AtlasDriver

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes run driver."""

        # Initialize parent class
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

    def run(self, *args: Any, **kwargs: Any) -> None:
        """Runs driver."""

        # Run parent class
        super().run(*args, **kwargs)

        # Initialize driver
        self.driver = self.Driver(
            name=self.args.name,
            bus=self.bus,
            address=self.address,
            mux=self.mux,
            channel=self.channel,
        )

        # Check if reading info
        if self.args.info:
            print(self.driver.read_info())

        # Check if reading status
        elif self.args.status:
            print(self.driver.read_status())

        # Check if enabling protocol lock
        elif self.args.enable_plock:
            self.driver.enable_protocol_lock()

        # Check if disabling protocol lock
        elif self.args.disable_plock:
            self.driver.disable_protocol_lock()

        # Check if enabling led
        elif self.args.enable_led:
            self.driver.enable_led()

        # Check if disabling led
        elif self.args.disable_led:
            self.driver.disable_led()

        # Check if reading status
        elif self.args.sleep:
            self.driver.enable_sleep_mode()


# Run main
if __name__ == "__main__":
    dr = DriverRunner()
    dr.run()
