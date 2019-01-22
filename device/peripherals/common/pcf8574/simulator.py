# Import python types
from typing import Any, Dict, Optional

# Import device utilities
from device.utilities.bitwise import byte_str

# Import simulator elements
from device.utilities.communication.i2c.peripheral_simulator import PeripheralSimulator


class PCF8574Simulator(PeripheralSimulator):  # type: ignore
    """Simulates communication with peripheral."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes simulator."""

        # Intialize parent class
        super().__init__(*args, **kwargs)

        # Initialize registers and write dicts
        self.registers: Dict = {}
        self.writes: Dict = {}

        # Initialize port byte
        self.port_status_byte = 0x00

    def get_write_response_bytes(self, write_bytes: bytes) -> Optional[bytes]:
        """Gets response byte for write command. Handles state based writes. This driver
        will only ever write 1 byte to the deivce that corresponds to the port status 
        byte."""
        self.port_status_byte = write_bytes[0]
        return bytes([0x00])  # TODO: Check was is returned from the hardware function

    def get_read_response_bytes(self, num_bytes: int) -> bytes:
        """Gets response bytes from read command. Handles state based reads. This 
        driver will only ever read 1 byte from the device. That byte corresponds to 
        the port status byte."""
        return bytes([self.port_status_byte])
