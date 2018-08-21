from device.comms.i2c2.peripheral_simulator import PeripheralSimulator
from device.utilities.bitwise import byte_str


class AtlasPHSimulator(PeripheralSimulator):
    """Simulates communication with atlas pH sensor."""

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.registers = {}
        self.writes = {}

        # ABC_LOGIC_WRITE_BYTES = bytes([0x05, 0x03, 0xEE, 0xFF, 0x00])
        # ABC_LOGIC_RESPONSE_BYTES = bytes([])

        # STATUS_WRITE_BYTES = bytes([0x04, 0x13, 0x8A, 0x00, 0x01])
        # STATUS_RESPONSE_BYTES = bytes([])

        # CO2_WRITE_BYTES = bytes([0x04, 0x13, 0x8B, 0x00, 0x01])
        # CO2_RESPONSE_BYTES = bytes([0x04, 0x02, 0x02, 0x22])

        # self.writes = {
        #     byte_str(ABC_LOGIC_WRITE_BYTES): ABC_LOGIC_RESPONSE_BYTES,
        #     byte_str(STATUS_WRITE_BYTES): STATUS_RESPONSE_BYTES,
        #     byte_str(CO2_WRITE_BYTES): CO2_RESPONSE_BYTES,
        # }
