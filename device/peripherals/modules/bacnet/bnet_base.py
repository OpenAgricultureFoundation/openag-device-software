# Abstract base class for wrapping and simulating BACnet communications using
# the pacpypes module.

from abc import ABC, abstractmethod    

class BnetBase(ABC):

    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass

    @abstractmethod
    def ping(self) -> None:
        pass

    @abstractmethod
    def set_test_voltage(self, voltage: float) -> None:
        pass

    @abstractmethod
    def set_air_temp(self, tempC: float) -> None:
        pass

    @abstractmethod
    def set_air_RH(self, RH: float) -> None:
        pass

    @abstractmethod
    def get_air_temp(self) -> float:
        pass

    @abstractmethod
    def get_air_RH(self) -> float:
        pass
