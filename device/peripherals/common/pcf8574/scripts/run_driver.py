# Import standard python modules
import os, sys, threading

# Import python types
from typing import Any, Dict

# Set system path
sys.path.append(str(os.getenv("PROJECT_ROOT", "")))


# Import run peripheral parent class
from device.peripherals.classes.peripheral.scripts.run_peripheral import RunnerBase

# Import peripheral driver
from device.peripherals.common.pcf8574.driver import PCF8574Driver


class DriverRunner(RunnerBase):  # type: ignore
    """Runs driver."""

    # Initialize defaults
    default_device = "fermentabot-v0.1.0"
    default_name = "OpenAgHeater300v1-Side"

    # Initialize var types
    communication: Dict[str, Any]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes run driver."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize parser
        self.parser.add_argument("--port", type=int, help="set port (0-7)")
        self.parser.add_argument("--high", action="store_true", help="set output high")
        self.parser.add_argument("--low", action="store_true", help="set output low")

    def run(self, *args: Any, **kwargs: Any) -> None:
        """Runs driver."""

        # Run parent class
        super().run(*args, **kwargs)

        # Initialize driver optional mux parameter
        mux = self.communication.get("mux", None)
        if mux != None:
            mux = int(mux, 16)

        # Initialize driver
        self.driver = DAC5578Driver(
            name=self.args.name,
            i2c_lock=threading.RLock(),
            bus=self.communication["bus"],
            address=int(self.communication["address"], 16),
            mux=mux,
            channel=self.communication.get("channel", None),
        )

        # Check if setting a channel to a value
        if self.args.port == None:
            print("Please specify a port")
            return

        # Check if setting high
        elif self.args.high:
            self.driver.set_high(self.args.port)

        # Check if setting low
        elif self.args.low:
            self.driver.set_low(self.args.port)


# Run main
if __name__ == "__main__":
    dr = DriverRunner()
    dr.run()
