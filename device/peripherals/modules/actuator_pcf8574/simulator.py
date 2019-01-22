# Import python types
from typing import Any

# Import device utilities
from device.utilities.bitwise import byte_str

# Import simulator elements
from device.utilities.communication.i2c.peripheral_simulator import (
    PeripheralSimulator,
    verify_mux,
)


class SHT25Simulator(PeripheralSimulator):  # type: ignore
    """Simulates communication with sht25 sensor."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:

        super().__init__(*args, **kwargs)

        self.registers = {0xE7: 0x00}  # user register

        TEMPERATURE_WRITE_BYTES = bytes([0xF3])
        TEMPERATURE_RESPONSE_BYTES = bytes([0x67, 0x30])

        HUMIDITY_WRITE_BYTES = bytes([0xF5])
        HUMIDITY_RESPONSE_BYTES = bytes([0x9A, 0xA2])

        RESET_WRITE_BYTES = bytes([0xFE])
        RESET_RESPONSE_BYTES = bytes([])

        self.writes = {
            byte_str(TEMPERATURE_WRITE_BYTES): TEMPERATURE_RESPONSE_BYTES,
            byte_str(HUMIDITY_WRITE_BYTES): HUMIDITY_RESPONSE_BYTES,
            byte_str(RESET_WRITE_BYTES): RESET_RESPONSE_BYTES,
        }
