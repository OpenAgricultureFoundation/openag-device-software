# Import standard python libraries
import os, sys

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import run peripheral parent class
from device.peripherals.classes.peripheral_runner import PeripheralRunner

# Import device utilities
from device.utilities.accessors import get_peripheral_config

# Import driver
from device.peripherals.modules.sht25.driver import SHT25Driver


class DriverRunner(PeripheralRunner):
    """Runs driver."""

    def __init__(self, *args, **kwargs):
        """Initializes run driver."""
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

    def run(self, *args, **kwargs):
        """Runs driver."""
        super().run(*args, **kwargs)

        # Initialize driver
        self.driver = SHT25Driver(
            name=self.args.name,
            bus=self.communication["bus"],
            address=int(self.communication["address"], 16),
            mux=int(self.communication["mux"], 16),
            channel=self.communication["channel"],
        )

        # Check if reading temperature
        if self.args.temperature:
            print("Reading temperature")
            temperature = self.driver.read_temperature()
            print("Temperature: {} C".format(temperature))

        # Check if reading humidity
        elif self.args.humidity:
            print("Reading humidity")
            humidity = self.driver.read_humidity()
            print("Humidity: {} %".format(humidity))

        # Check if reading user register
        elif self.args.user_register:
            print("Reading user register")
            user_register = self.driver.read_user_register()
            print(user_register)


# Run main
if __name__ == "__main__":
    dr = DriverRunner()
    dr.run()
