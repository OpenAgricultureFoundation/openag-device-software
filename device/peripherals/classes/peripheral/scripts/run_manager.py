# Import standard python libraries
import os, sys, logging

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import typing modules
from typing import Any

# Import runner base class
from device.peripherals.classes.peripheral.scripts.run_peripheral import RunnerBase

# Import device utilities
from device.utilities.accessors import get_peripheral_config

# Import device state
from device.utilities.state.main import State

# Import peripheral manager
from device.peripherals.classes.peripheral.manager import PeripheralManager


class ManagerRunnerBase(RunnerBase):  # type: ignore
    """Runs manager."""

    # Initialize peripheral manager
    Manager = PeripheralManager

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes manager runner base class."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize parser
        self.parser.add_argument("--setup", action="store_true", help="updates")
        self.parser.add_argument("--update", action="store_true", help="updates")
        self.parser.add_argument("--reset", action="store_true", help="resets")
        self.parser.add_argument("--shutdown", action="store_true", help="shutsdown")

    def run(self, *args: Any, **kwargs: Any) -> None:
        """Runs driver."""

        # Run parent class
        super().run(*args, **kwargs)

        # Instantiate manager
        self.manager = self.Manager(
            name=self.args.name,
            i2c_lock=threading.RLock(),
            state=State(),
            config=self.peripheral_config,
        )

        # Initialize manager
        self.manager.initialize()

        # Check if setting up
        if self.args.setup:
            self.manager.setup()

        # Check if updating
        if self.args.update:
            self.manager.update()

        # Check if resetting
        if self.args.reset:
            self.manager.reset()

        # Check if shutting down
        if self.args.shutdown:
            self.manager.shutdown()


if __name__ == "__main__":
    runner = ManagerRunnerBase()
    runner.run()
