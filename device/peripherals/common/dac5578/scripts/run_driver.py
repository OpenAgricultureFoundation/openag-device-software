# Import standard python modules
import os, sys, threading

# Import python types
from typing import Any, Dict

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import run peripheral parent class
from device.peripherals.classes.peripheral.scripts.run_peripheral import RunnerBase

# Import peripheral driver
from device.peripherals.common.dac5578.driver import DAC5578Driver

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
    default_name = "LEDPanel-Top"

    # Initialize var types
    communication: Dict[str, Any]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes run driver."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize parser
        self.parser.add_argument("--panel-name", type=str, help="specify panel name")
        self.parser.add_argument("--channel", type=int, help="set channel (0-7)")
        self.parser.add_argument("--percent", type=int, help="set output (0-100)")
        self.parser.add_argument("--high", action="store_true", help="set output high")
        self.parser.add_argument("--low", action="store_true", help="set output low")
        self.parser.add_argument("--fade", action="store_true", help="fade low-high")
        self.parser.add_argument("--reset", action="store_true", help="resets device")

    def run(self, *args: Any, **kwargs: Any) -> None:
        """Runs driver."""

        # Run parent class
        super().run(*args, **kwargs)

        # Check if dac is used in led panel
        if "panels" in self.communication:

            # Check if panel name is specified
            if self.args.panel_name != None:

                # Check if panel name exists in list
                name = None
                for entry in self.communication["panels"]:
                    if entry["name"] == self.args.panel_name:
                        self.communication = entry
                        name = entry["name"]
                        break

                # Check if panel name was found
                if name == None:
                    print(
                        "Unable to find panel `{}`, using first entry instead".format(
                            self.args.panel_name
                        )
                    )
            else:
                # Default to using first panel in communication list
                self.communication = self.communication["panels"][0]

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
        if self.args.channel != None and self.args.percent != None:
            self.driver.write_output(self.args.channel, self.args.percent)

        # Check if setting all channels to a value
        elif self.args.channel == None and self.args.percent != None:
            outputs = {}
            for i in range(8):
                outputs[i] = self.args.percent
            self.driver.write_outputs(outputs)

        # Check if setting a channel or all channels high
        elif self.args.high:
            self.driver.set_high(channel=self.args.channel)

        # Check if setting a channel or all channels low
        elif self.args.low:
            self.driver.set_low(channel=self.args.channel)

        # Check if fading
        elif self.args.fade:
            self.driver.fade(cycles=10, channel=self.args.channel)

        # Check if resetting
        elif self.args.reset:
            self.driver.reset()


# Run main
if __name__ == "__main__":
    dr = DriverRunner()
    dr.run()
