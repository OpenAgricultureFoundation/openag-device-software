# Import python types
from typing import Any, Dict

# Import device utilities
from device.utilities.bitwise import byte_str

# Import simulator elements
from device.utilities.communication.i2c.peripheral_simulator import (
    PeripheralSimulator,
    verify_mux,
)


class CCS811Simulator(PeripheralSimulator):  # type: ignore
    """Simulates communication with sensor."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes simulator."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize registers
        self.registers: Dict = {}  # user register

        # # Initialize write and response bytes
        # EXAMPLE_WRITE_BYTES = bytes([0x00])
        # EXAMPLE_RESPONSE_BYTES = bytes([0x00, 0x00])

        # self.writes = {
        #     byte_str(EXAMPLE_WRITE_BYTES): EXAMPLE_RESPONSE_BYTES,
        # }
        self.writes: Dict = {}
