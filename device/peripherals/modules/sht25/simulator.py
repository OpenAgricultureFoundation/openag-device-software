from device.comms.i2c2.peripheral_simulator import PeripheralSimulator, verify_mux


class SHT25Simulator(PeripheralSimulator):
    """Simulates communication with sht25 sensor."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registers = {0xE7: 0x00}  # User register
        # self.write_bytes = {0xF3: []}
