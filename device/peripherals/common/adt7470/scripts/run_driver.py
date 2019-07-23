# Import standard python modules
import os, sys, threading

# Import python types
from typing import Any, Dict

# Set system path
sys.path.append(str(os.getenv("PROJECT_ROOT", "")))


# Import run peripheral parent class
from device.peripherals.classes.peripheral.scripts.run_peripheral import RunnerBase

# Import peripheral driver
from device.peripherals.common.adt7470.driver import ADT7470Driver


class DriverRunner(RunnerBase):  # type: ignore
    """Runs driver."""

    # Initialize defaults
    default_device = "pfc4-v0.1.0"
    default_name = "HeatSinkFanController"

    # Initialize var types
    communication: Dict[str, Any]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes run driver."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize parser
        self.parser.add_argument("--version", action="store_true", help="read version")
        self.parser.add_argument(
            "--enable-monitoring",
            action="store_true",
            help="enable temperature monitoring",
        )
        self.parser.add_argument(
            "--disable-monitoring",
            action="store_true",
            help="disable temperature monitoring",
        )
        self.parser.add_argument("--temperature", type=int, help="read temperature")
        self.parser.add_argument(
            "--max-temperature", action="store_true", help="read max temperature"
        )
        self.parser.add_argument(
            "--write-temperature-limits",
            action="store_true",
            help="write temperature limits",
        )
        self.parser.add_argument(
            "--shutdown", action="store_true", help="shutdown hardware"
        )

    def run(self, *args: Any, **kwargs: Any) -> None:
        """Runs driver."""

        # Run parent class
        super().run(*args, **kwargs)

        # Initialize driver
        self.driver = ADT7470Driver(
            name=self.args.name,
            i2c_lock=threading.RLock(),
            bus=self.bus,
            address=self.address,
            mux=self.mux,
            channel=self.channel,
        )

        # Check if reading version
        if self.args.version:
            self.driver.read_version()

        # Check if enabling monitoring
        elif self.args.enable_monitoring:
            self.driver.enable_monitoring()

        # Check if disabling monitoring
        elif self.args.disable_monitoring:
            self.driver.disable_monitoring()

        # Check if reading temperature
        elif self.args.temperature != None:
            self.driver.read_temperature(self.args.temperature)

        # Check if reading max temperature
        elif self.args.max_temperature:
            self.driver.read_max_temperature()

        # Check if writing temperature limits
        elif self.args.write_temperature_limits:
            self.driver.write_temperature_limits(0, 0, 40)

        # Check if shutting down
        elif self.args.shutdown:
            self.driver.shutdown()


# Run main
if __name__ == "__main__":
    driver_runner = DriverRunner()
    driver_runner.run()
