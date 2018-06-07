# Import standard python modules
from typing import Optional, Tuple, List, Dict
import time

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.error import Error

# Import peripheral event mixin
from device.peripherals.classes.peripheral_events import PeripheralEvents


class ELPUSB500W02ML21Events(PeripheralEvents):
    """ Event mixin for sht25 temperature and humidity sensor. """


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