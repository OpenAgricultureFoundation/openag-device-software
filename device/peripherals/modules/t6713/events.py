# Import standard python modules
from typing import Optional, Tuple, List, Dict

# Import device utilities
from device.utilities.modes import Modes

# Import peripheral event mixin
from device.peripherals.classes.peripheral.events import PeripheralEvents


class T6713Events(PeripheralEvents):  # type: ignore
    """Event mixin for manager."""

    def process_peripheral_specific_event(self, request: Dict) -> None:
        """Processes a peripheral specific event."""

        message = "Unknown event request type!"
        self.logger.info(message)
        self.response = {"status": 400, "message": message}
