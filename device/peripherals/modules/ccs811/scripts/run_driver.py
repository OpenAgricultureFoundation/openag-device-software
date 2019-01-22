# Import standard python modules
import os, sys, threading

# Import python types
from typing import Any

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import run peripheral parent class
from device.peripherals.classes.peripheral.scripts.run_peripheral import RunnerBase

# Import driver
from device.peripherals.modules.ccs811.driver import CCS811Driver


class DriverRunner(RunnerBase):  # type: ignore
    """Runs driver."""

    # Initialize defaults
    default_device = "edu-v0.2.0"
    default_name = "CCS811-Top"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes run driver."""

        # Initialize parent class
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

    def run(self, *args: Any, **kwargs: Any) -> None:
        """Runs driver."""

        # Run parent class
        super().run(*args, **kwargs)

        # Initialize driver
        self.driver = CCS811Driver(
            name=self.args.name,
            i2c_lock=threading.RLock(),
            bus=self.bus,
            address=self.address,
            mux=self.mux,
            channel=self.channel,
        )

        # Check if setting up sensor
        if self.args.setup:
            self.driver.setup()

        # Check if reading co2/tvoc
        elif self.args.co2 or self.args.tvoc:
            co2, tvoc = self.driver.read_algorithm_data()
            print("CO2: {} ppm".format(co2))
            print("TVOC: {} ppm".format(tvoc))

        # Check if setting measurement mode
        elif self.args.mode != None:
            self.driver.write_measurement_mode(self.args.mode, False, False)

        # Check if reading status register
        elif self.args.status:
            print(self.driver.read_status_register())

        # Check if reading error register
        elif self.args.error:
            print(self.driver.read_error_register())

        # Check if resetting
        elif self.args.reset:
            self.driver.reset()

        # Check if checking hardware id
        elif self.args.check_hardware_id:
            self.driver.check_hardware_id()
            print("Hardware ID is Valid")

        # Check if starting app
        elif self.args.start_app:
            self.driver.start_app()


# Run main
if __name__ == "__main__":
    runner = DriverRunner()
    runner.run()
