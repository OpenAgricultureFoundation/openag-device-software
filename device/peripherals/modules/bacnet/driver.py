# Import standard python modules
import time, threading

# Import python types
from typing import NamedTuple, Optional, Dict

# Import device utilities
from device.utilities.logger import Logger

# Import driver elements
from device.peripherals.modules.bacnet import exceptions


class BacnetDriver:
    """Driver for BACNet communications to HVAC."""

#debugrob: fix here down
    # --------------------------------------------------------------------------
    # Constants 
    TEST_V = "av10"

    # --------------------------------------------------------------------------
    def __init__(
        self,
        name: str,
        simulate: bool = False,
        ini_file: str = None
    ) -> None:
        """Initializes bacpypes."""

        self.logger = Logger(name, __name__)

        if ini_file is None:
            raise exceptions.InitError(message="Missing ini file", 
                    logger=self.logger) 

        if simulate:
            self.logger.info("Simulating driver, debugrob")

        try:
            self.logger.info("Init driver bacpypes, debugrob")
            time.sleep(0.05)  # Wait 
        except Exception as e:
            raise exceptions.InitError(logger=self.logger) from e

    # --------------------------------------------------------------------------
    def setup(self) -> None:
        self.logger.info("setup, debugrob")

    # --------------------------------------------------------------------------
    def reset(self) -> None:
        self.logger.info("reset, debugrob")

    # --------------------------------------------------------------------------
    def shutdown(self) -> None:
        self.logger.info("shutdown, debugrob")

    # --------------------------------------------------------------------------
    def ping(self) -> None:
        self.logger.info("whois bacpypes, debugrob")

    # --------------------------------------------------------------------------
    def set_test_voltage(self, voltage: float) -> None:
        if voltage < 0.0 or voltage > 10.0:
            raise exceptions.DriverError(
                message=f"Test voltage {voltage} out of range (0-10)", 
                logger=self.logger)
        self.logger.info(f"set_test_voltage {voltage} bacpypes, debugrob")

    # --------------------------------------------------------------------------
    def set_air_temp(self, tempC: float) -> None:
        if tempC < -100.0 or tempC > 200.0:
            raise exceptions.DriverError(
                message=f"Air Temperature Celsius {tempC} out of range", 
                logger=self.logger)
        self.logger.info(f"set_air_temp {tempC} bacpypes, debugrob")

    # --------------------------------------------------------------------------
    def set_air_RH(self, RH: float) -> None:
        if RH < 0.0 or RH > 100.0:
            raise exceptions.DriverError(
                message=f"Relative Humidity {RH} out of range", 
                logger=self.logger)
        self.logger.info(f"set_air_RH {RH} bacpypes, debugrob")







