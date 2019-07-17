# Import standard python modules
import os, sys, threading

# Import python types
from typing import Any, Dict

# Set system path
sys.path.append(str(os.getenv("PROJECT_ROOT", "")))


# Import run peripheral parent class
from device.peripherals.classes.peripheral.scripts.run_peripheral import RunnerBase

# Import peripheral driver
from device.peripherals.common.pca9633.driver import PCA9633Driver


class DriverRunner(RunnerBase):  # type: ignore
    """Runs driver."""

    # Initialize defaults
    default_device = "pfc4-v0.1.0"
    default_name = "IndicatorLEDs"

    # Initialize var types
    communication: Dict[str, Any]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes run driver."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize parser
        self.parser.add_argument("--green", action="store_true", help="set green")
        self.parser.add_argument("--off", action="store_true", help="set off")

    def run(self, *args: Any, **kwargs: Any) -> None:
        """Runs driver."""

        # Run parent class
        super().run(*args, **kwargs)

        print(self.communication)

        # Initialize drivers
        self.drivers = []
        devices = self.communication.get("devices", [])
        for device in devices:

            # Initialize driver optional mux parameter
            mux = device.get("mux", None)
            if mux != None:
                mux = int(mux, 16)

            # Initialize driver
            self.drivers.append(
                PCA9633Driver(
                    name=device.get("name", "Default"),
                    i2c_lock=threading.RLock(),
                    bus=device["bus"],
                    address=int(device["address"], 16),
                    mux=mux,
                    channel=device.get("channel", None),
                )
            )

        # Check if setting green
        if self.args.green:
            for driver in self.drivers:
                driver.set_rgb([0, 255, 0])

        # Check if setting off
        elif self.args.off:
            for driver in self.drivers:
                driver.set_rgb([0, 0, 0])


# Run main
if __name__ == "__main__":
    dr = DriverRunner()
    dr.run()
