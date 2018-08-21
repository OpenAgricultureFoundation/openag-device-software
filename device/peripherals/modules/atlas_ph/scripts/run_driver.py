# Import standard python libraries
import os, sys

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import typing modules
from typing import Any

# Import device utilities
from device.utilities.accessors import get_peripheral_config

# Import driver modules
from device.peripherals.classes.atlas.scripts.run_driver import DriverRunner as AtlasDriverRunner
from device.peripherals.modules.atlas_ph.driver import AtlasPHDriver


class DriverRunner(AtlasDriverRunner):
    """Runs driver."""

    def __init__(self, *args: Any, **kwargs: Any):
        """Initializes run driver."""
        super().__init__(*args, **kwargs)

        # Initialize parser
        self.parser.add_argument("--ph", action="store_true", help="read pH")

    def initialize_driver(self):
        """Initializes driver instance."""

        # Initialize driver optional parameters
        mux = self.communication.get("mux", None)
        if mux != None:
            mux = int(mux, 16)

        # Initialize driver
        self.driver = AtlasPHDriver(
            name=self.args.name,
            bus=self.communication["bus"],
            address=int(self.communication["address"], 16),
            mux=mux,
            channel=self.communication.get("channel", None),
        )

    def run(self, *args: Any, **kwargs: Any):
        """Runs driver."""
        super().run(*args, **kwargs)

        # Check if reading pH
        if self.args.ph:
            print("Reading pH")
            ph = self.driver.read_ph()
            print("pH: {}".format(ph))


# Run main
if __name__ == "__main__":
    dr = DriverRunner()
    dr.run()
