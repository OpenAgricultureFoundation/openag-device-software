# Import standard python libraries
import os, sys, threading

# Import python types
from typing import Any

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import run peripheral parent class
from device.peripherals.classes.peripheral.scripts.run_peripheral import RunnerBase

# Import driver
from device.peripherals.modules.t6713.driver import T6713Driver


class DriverRunner(RunnerBase):  # type: ignore
    """Runs driver."""

    # Initialize defaults
    default_device = "edu-v0.1.0"
    default_name = "T6713-Top"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes run driver."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize parser
        self.parser.add_argument("--status", action="store_true", help="read status")
        self.parser.add_argument("--setup", action="store_true", help="sets up sensor")
        self.parser.add_argument("--co2", action="store_true", help="read co2")
        self.parser.add_argument("--reset", action="store_true", help="resets sensor")
        self.parser.add_argument(
            "--enable-abc", action="store_true", help="enables abc logic"
        )
        self.parser.add_argument(
            "--disable-abc", action="store_true", help="disables abc logic"
        )

    def run(self, *args: Any, **kwargs: Any) -> None:
        """Runs driver."""

        # Run parent class
        super().run(*args, **kwargs)

        # Initialize driver
        self.driver = T6713Driver(
            name=self.args.name,
            i2c_lock=threading.RLock(),
            bus=self.bus,
            address=self.address,
            mux=self.mux,
            channel=self.channel,
        )

        # Check if reading status
        if self.args.status:
            status = self.driver.read_status()
            print("Status: {}".format(status))

        # Check if setting up sensor
        if self.args.setup:
            self.driver.setup()

        # Check if reading carbon dioxide
        elif self.args.co2:
            co2 = self.driver.read_co2()
            print("Co2: {} ppm".format(co2))

        # Check if resetting sensor
        elif self.args.reset:
            self.driver.reset()

        # Check if enabling abc logic
        elif self.args.enable_abc:
            self.driver.enable_abc_logic()

        # Check if disabling abc logic
        elif self.args.disable_abc:
            self.driver.disable_abc_logic()


# Run main
if __name__ == "__main__":
    dr = DriverRunner()
    dr.run()
