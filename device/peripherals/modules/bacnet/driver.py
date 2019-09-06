# Import device utilities
from device.utilities.logger import Logger

# Import driver elements
from device.peripherals.modules.bacnet import exceptions

# Conditionally import the bacpypes wrapper class, or use the simulator.
# The brain that runs on PFCs doesn't have or need BACnet communications,
# only the LGHC (running on linux) does.
try:
    from device.peripherals.modules.bacnet import bnet_wrapper as bnet
except Exception as e:
    l = Logger("\n\nBACNet.driver", __name__)
    l.critical(e)
    from device.peripherals.modules.bacnet import bnet_simulator as bnet


class BacnetDriver:
    """Driver for BACNet communications to HVAC."""

    # --------------------------------------------------------------------------
    def __init__(
        self,
        name: str,
        simulate: bool = False,
        ini_file: str = None,
        debug: bool = False
    ) -> None:
        """Initializes bacpypes."""

        self.logger = Logger(name + ".BACNet", __name__)

        if ini_file is None:
            raise exceptions.InitError(message="Missing ini file", 
                    logger=self.logger) 

#debugrob: develop with real one, remove the comments later.
        """
        if simulate:
            from device.peripherals.modules.bacnet import bnet_simulator as bnet
        """

        try:
            self.logger.info("driver init")
            self.bnet = bnet.Bnet(self.logger, ini_file, debug)

        except Exception as e:
            raise exceptions.InitError(logger=self.logger) from e

    # --------------------------------------------------------------------------
    def setup(self) -> None:
        self.bnet.setup()

    # --------------------------------------------------------------------------
    def reset(self) -> None:
        self.bnet.reset()

    # --------------------------------------------------------------------------
    # This peripheral thread has been killed by the periph. manager. dead.
    def shutdown(self) -> None:
        self.logger.info("shutdown")

    # --------------------------------------------------------------------------
    def ping(self) -> None:
        self.bnet.ping()

    # --------------------------------------------------------------------------
    def set_test_voltage(self, voltage: float) -> None:
        if voltage < 0.0 or voltage > 10.0:
            raise exceptions.DriverError(
                message=f"Test voltage {voltage} out of range (0-10)", 
                logger=self.logger)
        self.bnet.set_test_voltage(voltage)

    # --------------------------------------------------------------------------
    def set_air_temp(self, tempC: float) -> None:
        if tempC < -100.0 or tempC > 200.0:
            raise exceptions.DriverError(
                message=f"Air Temperature Celsius {tempC} out of range", 
                logger=self.logger)
        self.bnet.set_air_temp(tempC)

    # --------------------------------------------------------------------------
    def set_air_RH(self, RH: float) -> None:
        if RH < 0.0 or RH > 100.0:
            raise exceptions.DriverError(
                message=f"Relative Humidity {RH} out of range", 
                logger=self.logger)
        self.bnet.set_air_RH(RH)







