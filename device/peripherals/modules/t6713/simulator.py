from device.comms.i2c2.peripheral_simulator import PeripheralSimulator


class T6713Simulator(PeripheralSimulator):
    """Simulates communication with sensor."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.registers = {0xE7: 0x00}  # user register
        # self.writes = {
        #     bytes([0xF3]): bytes([0x63, 0x48]), bytes([0xF5]): bytes([0x9A, 0x55])
        # }
