# Import python types
from typing import Optional, Tuple, List, Dict, Any

# Import peripheral event mixin
from device.peripherals.classes.peripheral.events import PeripheralEvents


class AtlasDOEvents(PeripheralEvents):  # type: ignore
    """Event mixin for manager."""

    def process_peripheral_specific_event(
        self, request: Dict[str, Any]
    ) -> Tuple[str, int]:
        """Processes peripheral specific events."""
        return "Unknown event request type", 400
