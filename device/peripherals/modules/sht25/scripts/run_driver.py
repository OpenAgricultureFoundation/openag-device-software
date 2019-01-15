# Import standard python modules
import os, sys, subprocess, threading

# Import python types
from typing import Any

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import run peripheral parent class
from device.peripherals.classes.peripheral.scripts.run_peripheral import RunnerBase

# Import driver
from device.peripherals.modules.sht25.driver import SHT25Driver

# Ensure virtual environment is activated
if os.getenv("VIRTUAL_ENV") == None:
    print("Please activate your virtual environment then re-run script")
    exit(0)

# Ensure platform info is sourced
if os.getenv("PLATFORM") == None:
    print("Please source your platform info then re-run script")
    exit(0)


class DriverRunner(RunnerBase):  # type: ignore
    """Runs driver."""

    # Initialize defaults
    default_device = "edu-v0.1.0"
    default_name = "SHT25-Top"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes run driver."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize parser
        self.parser.add_argument(
            "--temperature", action="store_true", help="read temperature"
        )
        self.parser.add_argument(
            "--humidity", action="store_true", help="read humidity"
        )
        self.parser.add_argument(
            "--user-register", action="store_true", help="read user register"
        )

    def run(self, *args: Any, **kwargs: Any) -> None:
        """Runs driver."""

        # Run parent class
        super().run(*args, **kwargs)

        # Initialize driver
        self.driver = SHT25Driver(
            name=self.args.name,
            i2c_lock=threading.RLock(),
            bus=self.bus,
            address=self.address,
            mux=self.mux,
            channel=self.channel,
        )

        # Check if reading temperature
        if self.args.temperature:
            temperature = self.driver.read_temperature()
            print("Temperature: {} C".format(temperature))

        # Check if reading humidity
        elif self.args.humidity:
            humidity = self.driver.read_humidity()
            print("Humidity: {} %".format(humidity))

        # Check if reading user register
        elif self.args.user_register:
            user_register = self.driver.read_user_register()
            print(user_register)


# Run main
if __name__ == "__main__":
    dr = DriverRunner()
    dr.run()
