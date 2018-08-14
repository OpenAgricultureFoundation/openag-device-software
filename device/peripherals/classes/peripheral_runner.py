# Import standard python modules
import sys, os, argparse, logging, glob, json
from typing import List

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import device comms
from device.comms.i2c import I2C

# Import device utilities
from device.utilities.accessors import get_peripheral_config


class PeripheralRunner:
    """Runs peripherals."""

    def __init__(self) -> None:
        """Initializes run peripheral."""

        # Set os directory
        self.root_dir = os.environ["OPENAG_BRAIN_ROOT"]
        os.chdir(self.root_dir)

        # Initialize parser
        self.parser = argparse.ArgumentParser(description="Test and debug script")
        self.parser.add_argument(
            "--loop", action="store_true", help="loop command prompt"
        )
        self.parser.add_argument(
            "--device", type=str, help="specifies device config file name"
        )
        self.parser.add_argument(
            "--devices",
            action="store_true",
            help="lists available device config file names",
        )
        self.parser.add_argument(
            "--name", type=str, help="specifies peripheral name in config"
        )
        self.parser.add_argument(
            "--names", action="store_true", help="lists available peripheral names"
        )

        # Initialize available device config names
        devices = glob.glob(self.root_dir + "/data/devices/*.json")
        devices.sort()
        self.devices: List[str] = []
        for device in devices:
            name = device.split("/")[-1].replace(".json", "")
            self.devices.append(name)

    def run(self) -> None:
        """Runs peripheral."""

        # Read in arguments
        self.args = self.parser.parse_args()

        # Initialize logger
        logging.basicConfig(level=logging.DEBUG)

        # Check if listing devices
        if self.args.devices:
            print("Devices:")
            for device in self.devices:
                print("  " + device)
            sys.exit(0)

        # Check for device config argument
        if self.args.device == None:
            print("Please specify a device configuration (list devices with --devices)")
            sys.exit(0)

        # Check for existing device config
        if self.args.device not in self.devices:
            print("Invalid device config name (list devices with --devices)")
            sys.exit(0)

        # Load in device config
        self.device_config = json.load(
            open("data/devices/{}.json".format(self.args.device))
        )

        # Get available peripheral names
        self.names: List[str] = []
        for peripheral in self.device_config["peripherals"]:
            self.names.append(peripheral["name"])
        self.names.sort()

        # Check if listing peripheral names
        if self.args.names:
            print("Peripheral names:")
            for name in self.names:
                print("  " + name)
            sys.exit(0)

        # Check for peripheral name argument
        if self.args.name == None:
            print("Please specify a peripheral name (list names with --names")
            sys.exit(0)

        # Check for valid peripheral name
        if self.args.name not in self.names:
            print("Invalid peripheral name (list names with --names)")
            sys.exit(0)

        # Initialize peripheral config
        self.peripheral_config = get_peripheral_config(
            self.device_config["peripherals"], self.args.name
        )
        self.communication = self.peripheral_config["parameters"]["communication"]


if __name__ == "__main__":
    pr = PeripheralRunner()
    pr.run()
