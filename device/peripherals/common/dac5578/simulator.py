# Import python types
from typing import Any, Dict

# Import device utilities
from device.utilities.bitwise import byte_str

# Import simulator elements
from device.utilities.communication.i2c.peripheral_simulator import PeripheralSimulator


class DAC5578Simulator(PeripheralSimulator):  # type: ignore
    """Simulates communication with peripheral."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes simulator."""

        # Intialize parent class
        super().__init__(*args, **kwargs)

        self.registers: Dict = {}

        POWER_REGISTER_WRITE_BYTES = bytes([0x40])
        POWER_REGISTER_RESPONSE_BYTES = bytes([0x00, 0x00])

        self.writes = {
            byte_str(POWER_REGISTER_WRITE_BYTES): POWER_REGISTER_RESPONSE_BYTES
        }

        # Add all possible dac outputs to writes dict
        for channel in range(0x30, 0x37 + 1):
            for output in range(0x00, 0xFF + 1):
                OUTPUT_WRITE_BYTES = bytes([channel, output, 0x00])
                OUTPUT_RESPONSE_BYTES = bytes([])  # TODO
                self.writes[byte_str(OUTPUT_WRITE_BYTES)] = OUTPUT_RESPONSE_BYTES
