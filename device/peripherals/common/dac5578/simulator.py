# Import python types
from typing import Any, Dict

# Import device utilities
from device.utilities.bitwise import byte_str

# Import simulator elements
from device.comms.i2c2.peripheral_simulator import PeripheralSimulator


class DAC5578Simulator(PeripheralSimulator):  # type: ignore
    """Simulates communication with peripheral."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes simulator."""

        # Intialize parent class
        super().__init__(*args, **kwargs)

        self.registers: Dict = {}

        POWER_REGISTER_WRITE_BYTES = bytes([0x40])
        POWER_REGISTER_RESPONSE_BYTES = bytes([0x00, 0x00])

        OUTPUT_CH0_0_WRITE_BYTES = bytes([0x30, 0x00, 0x00])
        OUTPUT_CH0_0_RESPONSE_BYTES = bytes([])  # TODO

        OUTPUT_CH1_0_WRITE_BYTES = bytes([0x31, 0x00, 0x00])
        OUTPUT_CH1_0_RESPONSE_BYTES = bytes([])  # TODO

        OUTPUT_CH2_0_WRITE_BYTES = bytes([0x32, 0x00, 0x00])
        OUTPUT_CH2_0_RESPONSE_BYTES = bytes([])  # TODO

        OUTPUT_CH3_0_WRITE_BYTES = bytes([0x33, 0x00, 0x00])
        OUTPUT_CH3_0_RESPONSE_BYTES = bytes([])  # TODO

        OUTPUT_CH4_0_WRITE_BYTES = bytes([0x34, 0x00, 0x00])
        OUTPUT_CH4_0_RESPONSE_BYTES = bytes([])  # TODO

        OUTPUT_CH5_0_WRITE_BYTES = bytes([0x35, 0x00, 0x00])
        OUTPUT_CH5_0_RESPONSE_BYTES = bytes([])  # TODO

        OUTPUT_CH6_0_WRITE_BYTES = bytes([0x36, 0x00, 0x00])
        OUTPUT_CH6_0_RESPONSE_BYTES = bytes([])  # TODO

        OUTPUT_CH7_0_WRITE_BYTES = bytes([0x37, 0x00, 0x00])
        OUTPUT_CH7_0_RESPONSE_BYTES = bytes([])  # TODO

        OUTPUT_CH0_100_WRITE_BYTES = bytes([0x30, 0xFF, 0x00])
        OUTPUT_CH0_100_RESPONSE_BYTES = bytes([])  # TODO

        OUTPUT_CH1_100_WRITE_BYTES = bytes([0x31, 0xFF, 0x00])
        OUTPUT_CH1_100_RESPONSE_BYTES = bytes([])  # TODO

        OUTPUT_CH2_100_WRITE_BYTES = bytes([0x32, 0xFF, 0x00])
        OUTPUT_CH2_100_RESPONSE_BYTES = bytes([])  # TODO

        OUTPUT_CH3_100_WRITE_BYTES = bytes([0x33, 0xFF, 0x00])
        OUTPUT_CH3_100_RESPONSE_BYTES = bytes([])  # TODO

        OUTPUT_CH4_100_WRITE_BYTES = bytes([0x34, 0xFF, 0x00])
        OUTPUT_CH4_100_RESPONSE_BYTES = bytes([])  # TODO

        OUTPUT_CH5_100_WRITE_BYTES = bytes([0x35, 0xFF, 0x00])
        OUTPUT_CH5_100_RESPONSE_BYTES = bytes([])  # TODO

        OUTPUT_CH6_100_WRITE_BYTES = bytes([0x36, 0xFF, 0x00])
        OUTPUT_CH6_100_RESPONSE_BYTES = bytes([])  # TODO

        OUTPUT_CH7_100_WRITE_BYTES = bytes([0x37, 0xFF, 0x00])
        OUTPUT_CH7_100_RESPONSE_BYTES = bytes([])  # TODO

        self.writes = {
            byte_str(POWER_REGISTER_WRITE_BYTES): POWER_REGISTER_RESPONSE_BYTES,
            byte_str(OUTPUT_CH0_0_WRITE_BYTES): OUTPUT_CH0_0_RESPONSE_BYTES,
            byte_str(OUTPUT_CH1_0_WRITE_BYTES): OUTPUT_CH1_0_RESPONSE_BYTES,
            byte_str(OUTPUT_CH2_0_WRITE_BYTES): OUTPUT_CH2_0_RESPONSE_BYTES,
            byte_str(OUTPUT_CH3_0_WRITE_BYTES): OUTPUT_CH3_0_RESPONSE_BYTES,
            byte_str(OUTPUT_CH4_0_WRITE_BYTES): OUTPUT_CH4_0_RESPONSE_BYTES,
            byte_str(OUTPUT_CH5_0_WRITE_BYTES): OUTPUT_CH5_0_RESPONSE_BYTES,
            byte_str(OUTPUT_CH6_0_WRITE_BYTES): OUTPUT_CH6_0_RESPONSE_BYTES,
            byte_str(OUTPUT_CH7_0_WRITE_BYTES): OUTPUT_CH7_0_RESPONSE_BYTES,
            byte_str(OUTPUT_CH0_100_WRITE_BYTES): OUTPUT_CH0_100_RESPONSE_BYTES,
            byte_str(OUTPUT_CH1_100_WRITE_BYTES): OUTPUT_CH1_100_RESPONSE_BYTES,
            byte_str(OUTPUT_CH2_100_WRITE_BYTES): OUTPUT_CH2_100_RESPONSE_BYTES,
            byte_str(OUTPUT_CH3_100_WRITE_BYTES): OUTPUT_CH3_100_RESPONSE_BYTES,
            byte_str(OUTPUT_CH4_100_WRITE_BYTES): OUTPUT_CH4_100_RESPONSE_BYTES,
            byte_str(OUTPUT_CH5_100_WRITE_BYTES): OUTPUT_CH5_100_RESPONSE_BYTES,
            byte_str(OUTPUT_CH6_100_WRITE_BYTES): OUTPUT_CH6_100_RESPONSE_BYTES,
            byte_str(OUTPUT_CH7_100_WRITE_BYTES): OUTPUT_CH7_100_RESPONSE_BYTES,
        }
