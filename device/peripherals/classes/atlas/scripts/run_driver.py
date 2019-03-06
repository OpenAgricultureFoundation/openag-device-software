# Import standard python libraries
import os, sys, threading

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import type checks
from typing import Any

# Import run peripheral parent class
from device.peripherals.classes.peripheral.scripts.run_peripheral import RunnerBase

# Import device utilities
from device.utilities.accessors import get_peripheral_config

# Import driver
from device.peripherals.classes.atlas.driver import AtlasDriver


class DriverRunner(RunnerBase):  # type: ignore
    """Runs driver."""

    # Initialize driver class
    Driver = AtlasDriver

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes run driver."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize parser
        self.parser.add_argument("--info", action="store_true", help="read info")
        self.parser.add_argument("--status", action="store_true", help="read status")
        self.parser.add_argument("--setup", action="store_true", help="setup sensor")
        self.parser.add_argument(
            "--enable-plock", action="store_true", help="enables protocol lock"
        )
        self.parser.add_argument(
            "--disable-plock", action="store_true", help="disables protocol lock"
        )
        self.parser.add_argument(
            "--enable-led", action="store_true", help="enables led"
        )
        self.parser.add_argument(
            "--disable-led", action="store_true", help="disables led"
        )
        self.parser.add_argument(
            "--sleep", action="store_true", help="enable sleep mode"
        )
        self.parser.add_argument(
            "--set-temp", type=float, help="set compensation temperature in Celsius"
        )
        self.parser.add_argument(
            "--calibrate-low", type=float, help="take low point calibration reading"
        )
        self.parser.add_argument(
            "--calibrate-mid", type=float, help="take mid point calibration reading"
        )
        self.parser.add_argument(
            "--calibrate-high", type=float, help="take high point calibration reading"
        )
        self.parser.add_argument(
            "--calibrate-clear", action="store_true", help="clear calibration readings"
        )
        self.parser.add_argument(
            "--factory-reset", action="store_true", help="perform factory reset"
        )

    def run(self, *args: Any, **kwargs: Any) -> None:
        """Runs driver."""

        # Run parent class
        super().run(*args, **kwargs)

        # Initialize driver
        self.driver = self.Driver(
            name=self.args.name,
            i2c_lock=threading.RLock(),
            bus=self.bus,
            address=self.address,
            mux=self.mux,
            channel=self.channel,
        )

        # Check if reading info
        if self.args.info:
            print(self.driver.read_info())

        # Check if reading status
        elif self.args.status:
            print(self.driver.read_status())

        # Check if setting up sensor
        elif self.args.setup:
            print(self.driver.setup())

        # Check if enabling protocol lock
        elif self.args.enable_plock:
            self.driver.enable_protocol_lock()

        # Check if disabling protocol lock
        elif self.args.disable_plock:
            self.driver.disable_protocol_lock()

        # Check if enabling led
        elif self.args.enable_led:
            self.driver.enable_led()

        # Check if disabling led
        elif self.args.disable_led:
            self.driver.disable_led()

        # Check if reading status
        elif self.args.sleep:
            self.driver.enable_sleep_mode()

        # Check if taking low point calibration
        elif self.args.calibrate_low:
            self.driver.take_low_point_calibration_reading(
                float(self.args.calibrate_low)
            )

        # Check if taking mid point calibration
        elif self.args.calibrate_mid:
            self.driver.take_mid_point_calibration_reading(
                float(self.args.calibrate_mid)
            )

        # Check if taking low point calibration
        elif self.args.calibrate_high:
            self.driver.take_high_point_calibration_reading(
                float(self.args.calibrate_high)
            )

        # Check if clearing calibration
        elif self.args.calibrate_clear:
            self.driver.clear_calibration_readings()

        # Check if factory resetting
        elif self.args.factory_reset:
            self.driver.factory_reset()


# Run main
if __name__ == "__main__":
    dr = DriverRunner()
    dr.run()
