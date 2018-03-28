# Import python modules
import logging, time, threading, json, os, sys

# Import device modes, errors, and events
from device.utility.mode import Mode
from device.utility.error import Error
from device.utility.event import EventRequest
from device.utility.event import EventResponse

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
        """ Processes event when new model is saved in Event table. """
        event = EventModel.objects.latest()

        # Check if new event
        if event.response is not None:
            return
            
        # Initialize response
        event.response = {}

        # Verify request is valid
        if "type" not in event.request:
            event.response["type"] = EventResponse.INVALID_REQUEST
            event.save()
            return
        
        # Handle event
        if event.request["type"] == EventRequest.LOAD_RECIPE:
            self.load_recipe(event)
        elif event.request["type"] == EventRequest.STOP_RECIPE:
            self.stop_recipe(event)
        elif event.request["type"] == EventRequest.LOAD_CONFIG:
            self.load_config(event)
        else:
            event.response["type"] = EventResponse.INVALID_EVENT
            event.save()
        

    def load_recipe(self, event):
        """ Loads recipe. """
        self.logger.info("Loading Recipe")
        event.response["type"] = EventResponse.SUCCESS
        event.save()


    def stop_recipe(self, event):
        """ Stops recipe. """
        self.logger.info("Stopping Recipe")
        event.response["type"] = EventResponse.SUCCESS
        event.save()


    def load_config(self, event):
        """ Loads config. """
        self.logger.info("Loading Config")
        event.response["type"] = EventResponse.SUCCESS
        event.save()






