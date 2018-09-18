# Import python modules
import logging, time, threading, json, os, sys

# Import device utilities
from device.utilities.events import EventRequests
from device.utilities.events import EventResponses

# Import database models
from app.models import EventModel


class EventManager:
    """Manages events."""

    # Initialize vars
    timeout = 10  # seconds

    # Initialize logger
    extra = {"console_name": "Event", "file_name": "Event"}
    logger = logging.getLogger("event")
    logger = logging.LoggerAdapter(logger, extra)

    def __init__(self, state):
        """Initialize event manager."""
        self.logger.debug("Initializing manager")

        # Initialize state and stop event
        self.state = state
        self.stop_event = threading.Event()  # so we can stop this thread

    def spawn(self, delay=None):
        """ Spawns event thread. """
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.stop_event.set()

    def stopped(self):
        return self.stop_event.is_set()

    def run(self):
        """Runs event manager."""
        self.logger.info("Spawning event thread")
        while True:
            if self.stopped():
                break

            # Check for new event to process
            if EventModel.objects.filter(response=None).exists():
                event = EventModel.objects.filter(response=None).earliest()
                event.response = self.process(event.recipient, event.request)
                event.save()

            # Update every 100ms
            time.sleep(0.1)

    def process(self, recipient, request):
        """ Processes request to recipient, returns response. """
        self.logger.debug("Processing new event request")

        # Get request parameters
        try:
            recipient_type = recipient["type"]
            recipient_name = recipient["name"]
        except KeyError as e:
            self.logger.exception("Unable to get request parameters")
            response = {
                "status": 400,
                "message": "Unable to get request parameters: {}".format(e),
            }

        # Process device requests
        if recipient_type == "Device":
            self.logger.debug("Processing device event request")
            # Clear device response
            self.state.device["response"] = None

            # Send request to device
            self.state.device["request"] = request

            # Wait for response
            while self.state.device["response"] == None:
                # Check for timeout
                start_time = time.time()
                if time.time() - start_time > self.timeout:
                    message = "Request did not process within {} seconds".format(
                        self.timeout
                    )
                    self.logger.critical(message)
                    response = {"status": 500, "message": message}
                    return response

                # Update every 100ms
                time.sleep(0.1)

            # Return response
            response = self.state.device["response"]
            self.state.device["response"] = None
            return response

        # Process peripheral requests
        elif recipient_type == "Peripheral":
            self.logger.debug("Processing peripheral event request")

            # Check if recipient exists
            if recipient_name not in self.state.peripherals:
                response = {
                    "status": 400,
                    "message": "Peripheral recipient `{}` does not exist".format(
                        recipient_name
                    ),
                }
                return response

            # Clear peripheral response
            self.state.peripherals[recipient_name]["response"] = None

            # Send reqeust to peripheral
            self.state.peripherals[recipient_name]["request"] = request

            # Wait for response
            # This system is fragile....rework concept
            start_time = time.time()
            while self.state.peripherals[recipient_name]["response"] == None:

                # Check for timeout
                start_time = time.time()
                if time.time() - start_time > self.timeout:
                    message = "Request did not process within {} seconds".format(
                        self.timeout
                    )
                    self.logger.critical(message)
                    response = {"status": 500, "message": message}
                    return response

                # Update every 100ms
                time.sleep(0.1)

            # Return response
            response = self.state.peripherals[recipient_name]["response"]
            self.logger.debug("Returning response: {}".format(response))
            self.state.peripherals[recipient_name]["response"] = None
            return response

        else:
            # Return response
            response = {"status": 400, "message": "Unknown recipient"}
            return response
