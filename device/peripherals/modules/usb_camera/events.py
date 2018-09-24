# Import python types
from typing import Optional, Tuple, List, Dict, Any

# Import peripheral event mixin
from device.peripherals.classes.peripheral.events import PeripheralEvents


class USBCameraEvents(PeripheralEvents):  # type: ignore
    """Peripheral event handler."""

    def create_peripheral_specific_event(
        self, request: Dict[str, Any]
    ) -> Tuple[str, int]:
        """Processes peripheral specific event."""
        return "Unknown event request type", 400

    def check_peripheral_specific_events(self, request: Dict[str, Any]) -> None:
        """Checks peripheral specific events."""
        type_ = request.get("type")
        self.logger.error("Invalid event request type in queue: {}".format(type_))
