from device.comms.i2c2.peripheral_simulator import PeripheralSimulator


class T6713Simulator(PeripheralSimulator):
    """Simulates communication with t6713 sensor."""

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.registers = {}

        self.writes = {}
