# Import standard python libraries
import os, sys

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import run peripheral parent class
from device.peripherals.classes.peripheral_runner import PeripheralRunner

# Import device utilities
from device.utilities.accessors import get_peripheral_config

# Import driver
from device.peripherals.common.dac5578.driver import DAC5578


class DriverRunner(PeripheralRunner):
    """Runs driver."""

    def __init__(self, *args, **kwargs):
        """Initializes run driver."""
        super().__init__(*args, **kwargs)

        # Initialize parser
        self.parser.add_argument(
            "--panel-name", type=str, help="specifies panel name in config"
        )
        self.parser.add_argument("--probe", action="store_true", help="probes device")
        self.parser.add_argument("-c", "--channel", type=int, help="sets channel (0-7)")
        self.parser.add_argument(
            "-p", "--percent", type=int, help="sets output percent (0-100)"
        )
        self.parser.add_argument(
            "--high", action="store_true", help="outputs high voltage"
        )
        self.parser.add_argument(
            "--low", action="store_true", help="outputs low voltage"
        )
        self.parser.add_argument(
            "--fade", action="store_true", help="fades voltage x10 times"
        )
        self.parser.add_argument("--reset", action="store_true", help="resets device")

    def run(self, *args, **kwargs):
        """Runs driver."""
        super().run(*args, **kwargs)

        # Check is dac is used in led panel
        if "panels" in self.communication:

            # Default to using first panel in communication list
            self.communication = self.communication["panels"][0]

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
                        "Unable to find panel named `{}`, using first entry instead".format(
                            self.args.panel_name
                        )
                    )

        # Initialize driver optional mux parameter
        mux = self.communication.get("mux", None)
        if mux != None:
            mux = int(mux, 16)

        # Initialize driver
        self.driver = DAC5578(
            name=self.args.name,
            bus=self.communication["bus"],
            address=int(self.communication["address"], 16),
            mux=mux,
            channel=self.communication.get("channel", None),
        )

        # Check if probing
        if self.args.probe:
            print("Probing")
            error = self.driver.probe()
            if error.exists():
                print("error = {}".format(error.trace))
            else:
                print("Probe successful")

        # Check if setting a channel to a value
        elif self.args.channel != None and self.args.percent != None:
            print(
                "Setting channel {} to {}%".format(self.args.channel, self.args.percent)
            )
            error = self.driver.write_output(self.args.channel, self.args.percent)
            if error.exists():
                print("Error: {}".format(error.trace))

        # Check if setting all channels to a value
        elif self.args.channel == None and self.args.percent != None:
            print("Setting all channels to {}%".format(self.args.percent))

            outputs = {}
            for i in range(8):
                outputs[i] = self.args.percent

            error = self.driver.write_outputs(outputs)
            if error.exists():
                print("Error: {}".format(error.trace))

        # Check if setting a channel or all channels high
        elif self.args.high:
            print(
                "Setting {channel} high".format(
                    channel="all channels"
                    if self.args.channel == None
                    else "channel: " + str(self.args.channel)
                )
            )
            error = self.driver.set_high(channel=self.args.channel)
            if error.exists():
                print("Error: {}".format(error.trace))

        # Check if setting a channel or all channels low
        elif self.args.low:
            print(
                "Setting {channel} low".format(
                    channel="all channels"
                    if self.args.channel == None
                    else "channel: " + str(self.args.channel)
                )
            )
            error = self.driver.set_low(channel=self.args.channel)
            if error.exists():
                print("Error: {}".format(error.trace))

        # Check if fading
        elif self.args.fade:
            print(
                "Fading {channel}".format(
                    channel="all channels"
                    if self.args.channel == None
                    else "channel: " + str(self.args.channel)
                )
            )
            error = self.driver.fade(cycles=10, channel=self.args.channel)
            if error.exists():
                print("Error: {}".format(error.trace))

        # Check if resetting
        elif self.args.reset:
            print("Resetting")
            self.driver.reset()
            print("Reset successful")


# Run main
if __name__ == "__main__":
    dr = DriverRunner()
    dr.run()
