# Import python types
from typing import Any, Dict

# Import device utilities
from device.utilities.bitwise import byte_str

# Import peripheral simulator
from device.utilities.communication.i2c.peripheral_simulator import PeripheralSimulator


class T6713Simulator(PeripheralSimulator):  # type: ignore
    """Simulates communication with t6713 sensor."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:

        super().__init__(*args, **kwargs)

        self.registers: Dict = {}

        CO2_WRITE_BYTES = bytes([0x04, 0x13, 0x8B, 0x00, 0x01])
        CO2_RESPONSE_BYTES = bytes([0x04, 0x02, 0x02, 0x22])

        STATUS_WRITE_BYTES = bytes([0x04, 0x13, 0x8A, 0x00, 0x01])
        STATUS_RESPONSE_BYTES = bytes([])

        ENABLE_ABC_LOGIC_WRITE_BYTES = bytes([0x05, 0x03, 0xEE, 0xFF, 0x00])
        ENABLE_ABC_LOGIC_RESPONSE_BYTES = bytes([])

        DISABLE_ABC_LOGIC_WRITE_BYTES = bytes([0x05, 0x03, 0xEE, 0x00, 0x00])
        DISABLE_ABC_LOGIC_RESPONSE_BYTES = bytes([])

        self.writes = {
            byte_str(CO2_WRITE_BYTES): CO2_RESPONSE_BYTES,
            byte_str(STATUS_WRITE_BYTES): STATUS_RESPONSE_BYTES,
            byte_str(ENABLE_ABC_LOGIC_WRITE_BYTES): ENABLE_ABC_LOGIC_RESPONSE_BYTES,
            byte_str(DISABLE_ABC_LOGIC_WRITE_BYTES): DISABLE_ABC_LOGIC_RESPONSE_BYTES,
        }
