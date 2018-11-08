# Import python types
from typing import Any, Dict

# Import device utilities
from device.utilities.bitwise import byte_str

# Import simulator base clase
from device.peripherals.classes.atlas.simulator import AtlasSimulator


class AtlasTempSimulator(AtlasSimulator):  # type: ignore
    """Simulates communication with sensor."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """ Initializes simulator."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        self.registers: Dict = {}

        # Initialize write and response bytes
        TEMPERATURE_WRITE_BYTES = bytes([0x52, 0x00])
        TEMPERATURE_RESPONSE_BYTES = bytes(
            [
                0x01,
                0x32,
                0x32,
                0x2E,
                0x39,
                0x37,
                0x32,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
            ]
        )

        self.writes[byte_str(TEMPERATURE_WRITE_BYTES)] = TEMPERATURE_RESPONSE_BYTES
