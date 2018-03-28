# Import python modules
import logging, time, threading, json

# Import device modes and errors
from device.utility.mode import Mode
from device.utility.error import Error

# Initialize connection with django app
# import django, os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
# django.setup()

# Import database models
from app.models import Event as EventModel


class Event:
    """ Manages events. """

    # Initialize logger
    extra = {"console_name":"Event", "file_name": "event"}
    logger = logging.getLogger(__name__)
    logger = logging.LoggerAdapter(logger, extra)

    # Initialize mode & error variables
    _mode = None
    _error = None

    # Initialize thread object
    thread = None


    def __init__(self, state):
        """ Initialize event handler. """
        self.state = state
        self.mode = Mode.INIT
        self.error = Error.NONE


    def process(self, sender, instance, **kwargs):
        print("~~~~~~~~~~~~~~~~~~~~~~~~~")






