# Import python types
from typing import Dict, Any

# Import device utilities
from device.utilities.bitwise import byte_str
from device.utilities.communication.i2c.peripheral_simulator import (
    PeripheralSimulator,
    verify_mux,
)


ATLAS_SUCCESS_31 = bytes(
    [
        0x01,
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
        0x00,
        0x00,
        0x00,
    ]
)


class AtlasSimulator(PeripheralSimulator):  # type: ignore
    """Simulates communication with atlas sensors."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:

        super().__init__(*args, **kwargs)

        self.registers: Dict = {}

        INFO_WRITE_BYTES = bytes([0x69, 0x00])
        INFO_RESPONSE_BYTES = bytes(
            [
                0x01,
                0x3F,
                0x49,
                0x2C,
                0x45,
                0x43,
                0x2C,
                0x31,
                0x2E,
                0x39,
                0x36,
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

        STATUS_WRITE_BYTES = bytes([0x53, 0x74, 0x61, 0x74, 0x75, 0x73, 0x00])
        STATUS_RESPONSE_BYTES = bytes(
            [
                0x01,
                0x3F,
                0x53,
                0x54,
                0x41,
                0x54,
                0x55,
                0x53,
                0x2C,
                0x50,
                0x2C,
                0x33,
                0x2E,
                0x36,
                0x35,
                0x35,
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

        ENABLE_PLOCK_WRITE_BYTES = bytes(
            [0x50, 0x6C, 0x6F, 0x63, 0x6B, 0x2C, 0x31, 0x00]
        )
        ENABLE_PLOCK_RESPONSE_BYTES = ATLAS_SUCCESS_31

        DISABLE_PLOCK_WRITE_BYTES = bytes(
            [0x50, 0x6C, 0x6F, 0x63, 0x6B, 0x2C, 0x30, 0x00]
        )
        DISABLE_PLOCK_RESPONSE_BYTES = ATLAS_SUCCESS_31

        ENABLE_LED_WRITE_BYTES = bytes([0x4C, 0x2C, 0x31, 0x00])
        ENABLE_LED_RESPONSE_BYTES = ATLAS_SUCCESS_31

        DISABLE_LED_WRITE_BYTES = bytes([0x4C, 0x2C, 0x30, 0x00])
        DISABLE_LED_RESPONSE_BYTES = ATLAS_SUCCESS_31

        ENABLE_SLEEP_WRITE_BYTES = bytes([0x53, 0x6C, 0x65, 0x65, 0x70, 0x00])
        ENABLE_SLEEP_RESPONSE_BYTES = bytes([])

        SET_TEMP_26_WRITE_BYTES = bytes([0x54, 0x2C, 0x32, 0x36, 0x2E, 0x30, 0x00])
        SET_TEMP_26_RESPONSE_BYTES = ATLAS_SUCCESS_31

        CALIBRATE_LOW_4_WRITE_BYTES = bytes(
            [0x43, 0x61, 0x6C, 0x2C, 0x6C, 0x6F, 0x77, 0x2C, 0x34, 0x2E, 0x30, 0x00]
        )
        CALIBRATE_LOW_4_RESPONSE_BYTES = ATLAS_SUCCESS_31

        CALIBRATE_MID_7_WRITE_BYTES = bytes(
            [0x43, 0x61, 0x6C, 0x2C, 0x6D, 0x69, 0x64, 0x2C, 0x37, 0x2E, 0x30, 0x00]
        )
        CALIBRATE_MID_7_RESPONSE_BYTES = ATLAS_SUCCESS_31

        CALIBRATE_HIGH_10_WRITE_BYTES = bytes(
            [
                0x43,
                0x61,
                0x6C,
                0x2C,
                0x68,
                0x69,
                0x67,
                0x68,
                0x2C,
                0x31,
                0x30,
                0x2E,
                0x30,
                0x00,
            ]
        )
        CALIBRATE_HIGH_10_RESPONSE_BYTES = ATLAS_SUCCESS_31

        CLEAR_CALIBRATION_WRITE_BYTES = bytes(
            [0x43, 0x61, 0x6C, 0x2C, 0x63, 0x6C, 0x65, 0x61, 0x72, 0x00]
        )
        CLEAR_CALIBRATION_RESPONSE_BYTES = ATLAS_SUCCESS_31

        FACTORY_RESET_WRITE_BYTES = bytes(
            [0x46, 0x61, 0x63, 0x74, 0x6F, 0x72, 0x79, 0x00]
        )
        FACTORY_RESET_RESPONSE_BYTES = bytes([])

        self.writes = {
            byte_str(INFO_WRITE_BYTES): INFO_RESPONSE_BYTES,
            byte_str(STATUS_WRITE_BYTES): STATUS_RESPONSE_BYTES,
            byte_str(ENABLE_PLOCK_WRITE_BYTES): ENABLE_PLOCK_RESPONSE_BYTES,
            byte_str(DISABLE_PLOCK_WRITE_BYTES): DISABLE_PLOCK_RESPONSE_BYTES,
            byte_str(ENABLE_LED_WRITE_BYTES): ENABLE_LED_RESPONSE_BYTES,
            byte_str(DISABLE_LED_WRITE_BYTES): DISABLE_LED_RESPONSE_BYTES,
            byte_str(ENABLE_SLEEP_WRITE_BYTES): ENABLE_SLEEP_RESPONSE_BYTES,
            byte_str(SET_TEMP_26_WRITE_BYTES): SET_TEMP_26_RESPONSE_BYTES,
            byte_str(CALIBRATE_LOW_4_WRITE_BYTES): CALIBRATE_LOW_4_RESPONSE_BYTES,
            byte_str(CALIBRATE_MID_7_WRITE_BYTES): CALIBRATE_MID_7_RESPONSE_BYTES,
            byte_str(CALIBRATE_HIGH_10_WRITE_BYTES): CALIBRATE_HIGH_10_RESPONSE_BYTES,
            byte_str(CLEAR_CALIBRATION_WRITE_BYTES): CLEAR_CALIBRATION_RESPONSE_BYTES,
            byte_str(FACTORY_RESET_WRITE_BYTES): FACTORY_RESET_RESPONSE_BYTES,
        }
