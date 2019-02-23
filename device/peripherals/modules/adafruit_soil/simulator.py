# Import python types
from typing import Any

# Import device utilities
from device.utilities.bitwise import byte_str

# Import simulator elements
from device.utilities.communication.i2c.peripheral_simulator import (
    PeripheralSimulator,
    verify_mux,
)


class AdafruitSoilSimulator(PeripheralSimulator):  # type: ignore
    """Simulates communication with sht25 sensor."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:

        super().__init__(*args, **kwargs)

        # First byte is a base, 0x00 is the Status Base
        #                       0x0F is the Capacitive Touch Base
        TEMPERATURE_WRITE_BYTES = bytes([0x00, 0x04])
        TEMPERATURE_RESPONSE_BYTES = bytes([0x00, 0x18, 0x00, 0x00])  # 24.0

        HW_ID_WRITE_BYTES = bytes([0x00, 0x01])
        HW_ID_RESPONSE_BYTES = bytes([0x0F, 0xBA])  # 4026

        RESET_WRITE_BYTES = bytes([0x00, 0x7F])
        RESET_RESPONSE_BYTES = bytes([])

        MOISTURE_WRITE_BYTES = bytes([0x0F, 0x10])
        MOISTURE_RESPONSE_BYTES = bytes([0x03, 0xE8])  # 1000

        self.writes = {
            byte_str(TEMPERATURE_WRITE_BYTES): TEMPERATURE_RESPONSE_BYTES,
            byte_str(HW_ID_WRITE_BYTES): HW_ID_RESPONSE_BYTES,
            byte_str(RESET_WRITE_BYTES): RESET_RESPONSE_BYTES,
            byte_str(MOISTURE_WRITE_BYTES): MOISTURE_RESPONSE_BYTES,
        }
