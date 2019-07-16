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

        # # Initialize driver optional mux parameter
        # mux = self.communication.get("mux", None)
        # if mux != None:
        #     mux = int(mux, 16)

        # # Initialize driver
        # self.driver = PCA9633Driver(
        #     name=self.args.name,
        #     i2c_lock=threading.RLock(),
        #     bus=self.communication["bus"],
        #     address=int(self.communication["address"], 16),
        #     mux=mux,
        #     channel=self.communication.get("channel", None),
        # )

        # Initialize driver
        self.driver = PCA9633Driver(
            name=self.args.name, i2c_lock=threading.RLock(), bus=2, address=0x62
        )

        # Check if setting green
        if self.args.green:
            self.driver.set_rgb([0, 255, 0])

        # Check if setting off
        elif self.args.off:
            self.driver.set_rgb([0, 0, 0])


# Run main
if __name__ == "__main__":
    dr = DriverRunner()
    dr.run()
