# Import python types
from typing import Any, Dict

# Import device utilities
from device.utilities.bitwise import byte_str

# Import simulator base clase
from device.peripherals.classes.atlas.simulator import AtlasSimulator
from device.peripherals.classes.atlas.simulator import ATLAS_SUCCESS_31


class AtlasECSimulator(AtlasSimulator):  # type: ignore
    """Simulates communication with atlas EC sensor."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """ Initializes simulator."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        self.registers: Dict = {}

        # TODO: Simulator should take into account which outputs are enabled
        # Requires overwriting simulator read / write functions to add state

        EC_WRITE_BYTES = bytes([0x52, 0x00])
        EC_RESPONSE_BYTES = bytes(
            [
                0x01,
                0x30,
                0x2E,
                0x30,
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
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
            ]
        )

        ENABLE_EC_WRITE_BYTES = bytes([0x4F, 0x2C, 0x45, 0x43, 0x2C, 0x31, 0x00])
        ENABLE_EC_RESPONSE_BYTES = ATLAS_SUCCESS_31

        DISABLE_EC_WRITE_BYTES = bytes([0x4F, 0x2C, 0x45, 0x43, 0x2C, 0x30, 0x00])
        DISABLE_EC_RESPONSE_BYTES = ATLAS_SUCCESS_31

        ENABLE_TDS_WRITE_BYTES = bytes([0x4F, 0x2C, 0x54, 0x44, 0x53, 0x2C, 0x31, 0x00])
        ENABLE_TDS_RESPONSE_BYTES = ATLAS_SUCCESS_31

        DISABLE_TDS_WRITE_BYTES = bytes(
            [0x4F, 0x2C, 0x54, 0x44, 0x53, 0x2C, 0x30, 0x00]
        )
        DISABLE_TDS_RESPONSE_BYTES = ATLAS_SUCCESS_31

        ENABLE_SALINITY_WRITE_BYTES = bytes([0x4F, 0x2C, 0x53, 0x2C, 0x31, 0x00])
        ENABLE_SALINITY_RESPONSE_BYTES = ATLAS_SUCCESS_31

        DISABLE_SALINITY_WRITE_BYTES = bytes([0x4F, 0x2C, 0x53, 0x2C, 0x30, 0x00])
        DISABLE_SALINITY_RESPONSE_BYTES = ATLAS_SUCCESS_31

        ENABLE_SG_WRITE_BYTES = bytes([0x4F, 0x2C, 0x53, 0x47, 0x2C, 0x31, 0x00])
        ENABLE_SG_RESPONSE_BYTES = ATLAS_SUCCESS_31

        DISABLE_SG_WRITE_BYTES = bytes([0x4F, 0x2C, 0x53, 0x47, 0x2C, 0x30, 0x00])
        DISABLE_SG_RESPONSE_BYTES = ATLAS_SUCCESS_31

        SET_PROBE_1_WRITE_BYTES = bytes([0x4B, 0x2C, 0x31, 0x2E, 0x30, 0x00])
        SET_PROBE_1_RESPONSE_BYTES = ATLAS_SUCCESS_31

        CALIBRATE_DRY_WRITE_BYTES = bytes(
            [0x43, 0x61, 0x6C, 0x2C, 0x64, 0x72, 0x79, 0x00]
        )
        CALIBRATE_DRY_RESPONSE_BYTES = ATLAS_SUCCESS_31

        self.writes.update(
            {
                byte_str(EC_WRITE_BYTES): EC_RESPONSE_BYTES,
                byte_str(ENABLE_EC_WRITE_BYTES): ENABLE_EC_RESPONSE_BYTES,
                byte_str(DISABLE_EC_WRITE_BYTES): DISABLE_EC_RESPONSE_BYTES,
                byte_str(ENABLE_TDS_WRITE_BYTES): ENABLE_TDS_RESPONSE_BYTES,
                byte_str(DISABLE_TDS_WRITE_BYTES): DISABLE_TDS_RESPONSE_BYTES,
                byte_str(ENABLE_SALINITY_WRITE_BYTES): ENABLE_SALINITY_RESPONSE_BYTES,
                byte_str(DISABLE_SALINITY_WRITE_BYTES): DISABLE_SALINITY_RESPONSE_BYTES,
                byte_str(ENABLE_SG_WRITE_BYTES): ENABLE_SG_RESPONSE_BYTES,
                byte_str(DISABLE_SG_WRITE_BYTES): DISABLE_SG_RESPONSE_BYTES,
                byte_str(SET_PROBE_1_WRITE_BYTES): SET_PROBE_1_RESPONSE_BYTES,
                byte_str(CALIBRATE_DRY_WRITE_BYTES): CALIBRATE_DRY_RESPONSE_BYTES,
            }
        )
