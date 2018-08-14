# Import standard python libraries
import os, sys

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import run peripheral parent class
from device.peripherals.classes.peripheral_runner import PeripheralRunner

# Import device utilities
from device.utilities.accessors import get_peripheral_config

# Import driver
from device.peripherals.modules.ccs811.driver import CCS811Driver


class DriverRunner(PeripheralRunner):
    """Runs driver."""

    def __init__(self, *args, **kwargs):
        """Initializes run driver."""
        super().__init__(*args, **kwargs)

        # Initialize parser
        self.parser.add_argument("--setup", action="store_true", help="setup sensor")
        self.parser.add_argument("--co2", action="store_true", help="read co2")
        self.parser.add_argument("--tvoc", action="store_true", help="read tvoc")
        self.parser.add_argument("--mode", type=int, help="set device mode 1-4")
        self.parser.add_argument(
            "--status", action="store_true", help="read status register"
        )
        self.parser.add_argument(
            "--error", action="store_true", help="read error register"
        )
        self.parser.add_argument("--reset", action="store_true", help="resets sensor")
        self.parser.add_argument(
            "--check-hardware-id", action="store_true", help="checks hw id"
        )
        self.parser.add_argument("--start-app", action="store_true", help="starts app")

    def run(self, *args, **kwargs):
        """Runs driver."""
        super().run(*args, **kwargs)

        # Initialize driver
        self.driver = CCS811Driver(
            name=self.args.name,
            bus=self.communication["bus"],
            address=int(self.communication["address"], 16),
            mux=int(self.communication["mux"], 16),
            channel=self.communication["channel"],
        )

        # Check if setting up sensor
        if self.args.setup:
            print("Setting up sensor")
            self.driver.setup(retry=True)

        # Check if reading co2/tvoc
        elif self.args.co2 or self.args.tvoc:
            print("Reading co2/tvoc")
            co2, tvoc = self.driver.read_algorithm_data(retry=True)
            print("CO2: {} ppm".format(co2))
            print("TVOC: {} ppm".format(tvoc))

        # Check if setting measurement mode
        elif self.args.mode != None:
            print("Setting measurement mode")
            self.driver.write_measurement_mode(self.args.mode, False, False, retry=True)

        # Check if reading status register
        elif self.args.status:
            print("Reading status register")
            status_register = self.driver.read_status_register(retry=True)
            print(status_register)

        # Check if reading error register
        elif self.args.error:
            print("Reading error register")
            error_register = self.driver.read_error_register(retry=True)
            print(error_register)

        # Check if resetting
        elif self.args.reset:
            print("Resetting")
            self.driver.reset(retry=True)

        # Check if checking hardware id
        elif self.args.check_hardware_id:
            print("Checking hardware ID")
            self.driver.check_hardware_id(retry=True)
            print("Hardware ID is Valid")

        # Check if starting app
        elif self.args.start_app:
            print("Starting app")
            self.driver.start_app(retry=True)


# Run main
if __name__ == "__main__":
    dr = DriverRunner()
    dr.run()
