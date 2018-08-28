# Import python types
from typing import Optional, Tuple, List, Dict

# Import peripheral event mixin
from device.peripherals.classes.peripheral.events import PeripheralEvents


class SHT25Events(PeripheralEvents):  # type: ignore
    """ Event mixin for sht25 temperature and humidity sensor. """

    def process_peripheral_specific_event(self, request: Dict) -> None:
        """ Processes an event. Gets request parameters, executes request, returns 
            response. """

        message = "Unknown event request type"
        self.logger.info(message)
