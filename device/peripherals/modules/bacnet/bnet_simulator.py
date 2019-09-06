# Simulate BACnet communications 

from device.utilities.logger import Logger
from device.peripherals.modules.bacnet import bnet_base

class Bnet(bnet_base.BnetBase):

    def __init__(self, 
                 logger: Logger, 
                 ini_file: str = None, 
                 debug: bool = False
                 ) -> None:
        self.ini_file = ini_file
        self.debug = debug
        self.logger = logger
        self.logger.info("simulator init")

    def setup(self) -> None:
        self.logger.info("simulator setup")

    def reset(self) -> None:
        self.logger.info("simulator reset")

    def ping(self) -> None:
        self.logger.info("simulator ping, send whois message.")

    def set_test_voltage(self, voltage: float) -> None:
        self.logger.info(f"simulator set_test_voltage {voltage}")

    def set_air_temp(self, tempC: float) -> None:
        self.logger.info(f"simulator set_air_temp {tempC}")

    def set_air_RH(self, RH: float) -> None:
        self.logger.info(f"simulator set_air_RH {RH}")
