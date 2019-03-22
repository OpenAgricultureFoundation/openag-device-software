# Import python types
from typing import Any, Dict

# Import device utilities
from device.utilities.bitwise import byte_str

# Import simulator elements
from device.utilities.communication.i2c.peripheral_simulator import PeripheralSimulator

# Import driver elements
from device.peripherals.modules.actuator_grove_rgb_lcd import driver


class GroveRGBLCDSimulator(PeripheralSimulator):  # type: ignore
    """Simulates communication with peripheral."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes simulator."""

        # Intialize parent class
        super().__init__(*args, **kwargs)

        # No I2C registers used for this device
        self.registers: Dict = {}

        # LCD commands
        WRITE_BYTES = bytes(
            [driver.GroveRGBLCDDriver.CMD, driver.GroveRGBLCDDriver.CLEAR]
        )
        RESPONSE_BYTES = bytes([0x00, 0x00])
        self.writes = {byte_str(WRITE_BYTES): RESPONSE_BYTES}

        WRITE_BYTES = bytes(
            [
                driver.GroveRGBLCDDriver.CMD,
                driver.GroveRGBLCDDriver.DISPLAY_ON_NO_CURSOR,
            ]
        )
        self.writes[byte_str(WRITE_BYTES)] = RESPONSE_BYTES

        WRITE_BYTES = bytes(
            [driver.GroveRGBLCDDriver.CMD, driver.GroveRGBLCDDriver.TWO_LINES]
        )
        self.writes[byte_str(WRITE_BYTES)] = RESPONSE_BYTES

        WRITE_BYTES = bytes(
            [driver.GroveRGBLCDDriver.CMD, driver.GroveRGBLCDDriver.NEWLINE]
        )
        self.writes[byte_str(WRITE_BYTES)] = RESPONSE_BYTES

        # RGB commands
        WRITE_BYTES = bytes([0, 0])
        self.writes[byte_str(WRITE_BYTES)] = RESPONSE_BYTES
        WRITE_BYTES = bytes([1, 0])
        self.writes[byte_str(WRITE_BYTES)] = RESPONSE_BYTES
        WRITE_BYTES = bytes([0x08, 0xAA])
        self.writes[byte_str(WRITE_BYTES)] = RESPONSE_BYTES
        WRITE_BYTES = bytes([4, 0])
        self.writes[byte_str(WRITE_BYTES)] = RESPONSE_BYTES
        WRITE_BYTES = bytes([4, 0xFF])
        self.writes[byte_str(WRITE_BYTES)] = RESPONSE_BYTES
        WRITE_BYTES = bytes([3, 0])
        self.writes[byte_str(WRITE_BYTES)] = RESPONSE_BYTES
        WRITE_BYTES = bytes([3, 0xFF])
        self.writes[byte_str(WRITE_BYTES)] = RESPONSE_BYTES
        WRITE_BYTES = bytes([2, 0])
        self.writes[byte_str(WRITE_BYTES)] = RESPONSE_BYTES
        WRITE_BYTES = bytes([2, 0xFF])
        self.writes[byte_str(WRITE_BYTES)] = RESPONSE_BYTES
