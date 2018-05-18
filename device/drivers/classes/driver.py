# Import standard python modules
import logging, time

# Import health manager
from device.utilities.health import Health



# TODO: delete this.....until we have another driver class type


class Driver:
    """ A device driver for the lowest level of hardware interactions with an IC. """
    health = Health()
    name = None

    
    def __init__(self):

        # Initialize logger
        extra = {'console_name':self.name, 'file_name': self.name}
        logger = logging.getLogger(__name__)
        self.logger = logging.LoggerAdapter(logger, extra)


    def check_health(self):
        raise NotImplementedError()



