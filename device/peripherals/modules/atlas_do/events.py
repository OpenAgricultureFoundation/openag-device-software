# Import standard python modules
from typing import Optional, Tuple, List, Dict
import time

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.error import Error

# Import peripheral event mixin
from device.peripherals.classes.peripheral_events import PeripheralEvents


class AtlasDOEvents(PeripheralEvents):
    """ Event mixin for atlas dissolved oxygen sensor. """


    def process_peripheral_specific_event(self, request: Dict) -> Dict:
        """ Processes an event. Gets request parameters, executes request,
            sets response in shared state. """

        # Execute request
        if request["type"] == "New event":
            # self.response = self.process_new_event()
            ...
        else:
            message = "Unknown event request type!"
            self.logger.info(message)
            self.response = {"status": 400, "message": message}
