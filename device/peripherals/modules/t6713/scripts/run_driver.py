# Import standard python libraries
import sys, os, json, argparse, logging, time, shlex

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import run peripheral parent class
from device.peripherals.classes.peripheral_runner import PeripheralRunner

# Import device utilities
from device.utilities.accessors import get_peripheral_config

# Import driver
from device.peripherals.modules.t6713.driver import T6713Driver


class DriverRunner(PeripheralRunner):
    """Runs driver."""

    def __init__(self, *args, **kwargs):
        """Initializes run driver."""
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

    def run(self, *args, **kwargs):
        """Runs driver."""
        super().run(*args, **kwargs)

        # Initialize driver
        self.driver = T6713Driver(
            name=self.args.name,
            bus=self.communication["bus"],
            address=int(self.communication["address"], 16),
            mux=int(self.communication["mux"], 16),
            channel=self.communication["channel"],
        )

        # Check if reading status
        if self.args.status:
            print("Reading status")
            status = driver.read_status(retry=True)
            print("Status: {}".format(status))

        # Check if setting up sensor
        if self.args.setup:
            print("Setting up sensor")
            driver.setup(retry=True)

        # Check if reading carbon dioxide
        elif self.args.co2:
            print("Reading co2")
            co2 = driver.read_co2(retry=True)
            print("Co2: {} ppm".format(co2))

        # Check if resetting sensor
        elif self.args.reset:
            print("Resetting")
            driver.reset(retry=True)

        # Check if enabling abc logic
        elif self.args.enable_abc:
            print("Enabling abc logic")
            driver.enable_abc_logic(retry=True)

        # Check if disabling abc logic
        elif self.args.disable_abc:
            print("Disabling abc logic")
            driver.disable_abc_logic(retry=True)


# Run main
if __name__ == "__main__":
    dr = DriverRunner()
    dr.run()
