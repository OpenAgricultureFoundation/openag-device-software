# Import standard python modules
import sys, os, argparse, logging, glob, json

# Import python types
from typing import List

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import device utilities
from device.utilities.accessors import get_peripheral_config


class RunnerBase:
    """Runner base class."""

    # Initialize defaults
    default_device = None
    default_name = None
    default_log_level = logging.DEBUG

    def __init__(self) -> None:
        """Initializes run peripheral."""

        # Set os directory
        self.root_dir = os.environ["PROJECT_ROOT"]
        os.chdir(self.root_dir)

        # Initialize parser
        self.parser = argparse.ArgumentParser(description="Test and debug script")
        self.parser.add_argument(
            "--default", action="store_true", help="use default device and name"
        )
        self.parser.add_argument("--log-level", type=str, help="set logging level")
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
        if self.args.log_level:
            logging.basicConfig(level=getattr(logging, self.args.log_level))
        else:
            logging.basicConfig(level=self.default_log_level)

        # Check if using defaults
        if self.args.default:

            # Check if defaults are set
            if self.default_device == None or self.default_name == None:
                print("Defaults are not setup")
                sys.exit(0)

            # Set defaults
            self.args.device = self.default_device
            self.args.name = self.default_name

        # Check if listing devices
        if self.args.devices:
            print("Devices:")
            for device in self.devices:
                print("  " + device)
            sys.exit(0)

        # Check for device config argument
        if self.args.device == None:
            print("Please specify a device configuration or use --default")
            print("Note: you can list available device configs with --devices")
            sys.exit(0)

        # Check for existing device config
        if self.args.device not in self.devices:
            print("Invalid device config name")
            print("Note: you can list devices with --devices)")
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
            print("Please specify a peripheral name or use --default")
            print("Note: you can list names with --names")
            sys.exit(0)

        # Check for valid peripheral name
        if self.args.name not in self.names:
            print("Invalid peripheral name")
            print("Note: you can list names with --names)")
            sys.exit(0)

        # Initialize peripheral config
        self.peripheral_config = get_peripheral_config(
            self.device_config["peripherals"], self.args.name
        )

        # Initialize peripheral setup
        setup_name = self.peripheral_config["parameters"]["setup"]["file_name"]
        self.peripheral_setup = json.load(
            open("device/peripherals/modules/" + setup_name + ".json")
        )

        # Initialize parameters if exist
        self.parameters = self.peripheral_config.get("parameters", {})

        # Initialize communication if exists
        self.communication = self.parameters.get("communication", {})
        if self.communication == None:
            self.communication = {}

        # Initialize standard i2c config parameters if they exist
        self.bus = self.communication.get("bus", None)
        self.address = self.communication.get("address", None)
        self.mux = self.communication.get("mux", None)
        self.channel = self.communication.get("channel", None)

        # Convert i2c config params from hex to int if they exist
        if self.address != None:
            self.address = int(self.address, 16)
        if self.mux != None:
            self.mux = int(self.mux, 16)


if __name__ == "__main__":
    runner = RunnerBase()
    runner.run()
