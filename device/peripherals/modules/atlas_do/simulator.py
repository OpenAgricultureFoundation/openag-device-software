# Import python types
from typing import Any, Dict

# Import device utilities
from device.utilities.bitwise import byte_str

# Import simulator base clase
from device.peripherals.classes.atlas.simulator import AtlasSimulator


class AtlasDOSimulator(AtlasSimulator):  # type: ignore
    """Simulates communication with sensor."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """ Initializes simulator."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        self.registers: Dict = {}

        # # Initialize write and response bytes
        # EXAMPLE_WRITE_BYTES = bytes([0x00])
        # EXAMPLE_RESPONSE_BYTES = bytes([0x00, 0x00])

        # self.writes[byte_str(EXAMPLE_WRITE_BYTES)] = EXAMPLE_RESPONSE_BYTES
