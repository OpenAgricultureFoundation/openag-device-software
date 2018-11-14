# Import python types
from typing import Any, Dict

# Import device utilities
from device.utilities.bitwise import byte_str

# Import simulator base clase
from device.peripherals.classes.atlas.simulator import AtlasSimulator, ATLAS_SUCCESS_31


class AtlasCo2Simulator(AtlasSimulator):  # type: ignore
    """Simulates communication with sensor."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """ Initializes simulator."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        self.registers: Dict = {}

        # Initialize write and response bytes
        CO2_WRITE_BYTES = bytes([0x52, 0x00])
        CO2_RESPONSE_BYTES = bytes(
            [
                0x01,
                0x35,
                0x30,
                0x38,
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
                0x00,
                0x00,
                0x00,
            ]
        )
        self.writes[byte_str(CO2_WRITE_BYTES)] = CO2_RESPONSE_BYTES

        # Read internal temperature
        READ_TEMP_WRITE_BYTES = bytes([0x52, 0x00])
        READ_TEMP_RESPONSE_BYTES = bytes(
            [
                0x01,
                0x34,
                0x39,
                0x30,
                0x2C,
                0x32,
                0x37,
                0x2E,
                0x35,
                0x36,
                0x37,
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
        self.writes[byte_str(READ_TEMP_WRITE_BYTES)] = READ_TEMP_RESPONSE_BYTES

        # Sensor info
        INFO_WRITE_BYTES = bytes([0x69, 0x00])
        INFO_RESPONSE_BYTES = bytes(
            [
                0x01,
                0x3F,
                0x49,
                0x2C,
                0x43,
                0x4F,
                0x32,
                0x2C,
                0x31,
                0x2E,
                0x30,
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
        self.writes[byte_str(INFO_WRITE_BYTES)] = INFO_RESPONSE_BYTES

        # Enable internal temperature
        ENABLE_TEMP_WRITE_BYTES = bytes([0x4F, 0x2C, 0x74, 0x2C, 0x31, 0x00])
        ENABLE_TEMP_RESPONSE_BYTES = ATLAS_SUCCESS_31
        self.writes[byte_str(ENABLE_TEMP_WRITE_BYTES)] = ENABLE_TEMP_RESPONSE_BYTES

        # Disable internal temperature
        DISABLE_TEMP_WRITE_BYTES = bytes([0x4F, 0x2C, 0x74, 0x2C, 0x30, 0x00])
        DISABLE_TEMP_RESPONSE_BYTES = ATLAS_SUCCESS_31
        self.writes[byte_str(DISABLE_TEMP_WRITE_BYTES)] = DISABLE_TEMP_RESPONSE_BYTES

        # Disable alarm
        DISABLE_ALARM_WRITE_BYTES = bytes(
            [0x41, 0x6C, 0x61, 0x72, 0x6D, 0x2C, 0x65, 0x6E, 0x2C, 0x30, 0x00]
        )
        DISABLE_ALARM_RESPONSE_BYTES = ATLAS_SUCCESS_31
        self.writes[byte_str(DISABLE_ALARM_WRITE_BYTES)] = DISABLE_ALARM_RESPONSE_BYTES
