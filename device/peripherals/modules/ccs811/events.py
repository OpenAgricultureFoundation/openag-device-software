# Import standard python modules
from typing import Optional, Tuple, List, Dict
import time

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.error import Error

# Import peripheral event mixin
from device.peripherals.classes.peripheral_events import PeripheralEvents


class CCS811Events(PeripheralEvents):
    """ Event mixin for ccs811 co2 sensor. """

    def process_peripheral_specific_event(self, request: Dict) -> Dict:
        """ Processes an event. Gets request parameters, executes request, returns 
            response. """

        # Execute request
        if request["type"] == "New Event":
            # self.response = self.process_new_event()
            ...
        else:
            message = "Unknown event request type!"
            self.logger.info(message)
