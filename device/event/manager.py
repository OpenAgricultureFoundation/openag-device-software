# Import python modules
import logging, time, threading, json, os, sys

# Import python types
from typing import Dict, Any, Union

# Import device state
from device.state.main import State

# Import database models
from app.models import EventModel


class EventManager(object):
    """Manages events. Once thread is spawned, polls event table in database every 
    50 ms to check for latest entry without a response as an signifier for a new 
    request. Upon new request, forwards request to recipient (e.g. device coordinator, 
    specific peripheral, etc.) and wait for response with timeout."""

    # TODO: Use django signal for async db deltas instead of polling? What happens
    # with multiple quick requests?

    # Initialize vars
    timeout = 10  # seconds

    # Initialize logger
    extra = {"console_name": "Event", "file_name": "Event"}
    logger_raw = logging.getLogger("event")
    logger = logging.LoggerAdapter(logger_raw, extra)

    def __init__(self, state: State) -> None:
        """Initialize event manager."""
        self.logger.debug("Initializing manager")

        # Initialize state and stop event
        self.state = state
        self.stop_event = threading.Event()  # so we can stop this thread

    def spawn(self) -> None:
        """Spawns event thread."""
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def stop(self) -> None:
        """Stops thread."""
        self.stop_event.set()

    def stopped(self) -> bool:
        """Gets thread stop status."""
        return self.stop_event.is_set()

    def run(self) -> None:
        """Runs event manager."""
        self.logger.info("Spawning event thread")

        # Loop forever
        while True:

            # Check for new event to process
            if EventModel.objects.filter(response=None).exists():
                event = EventModel.objects.filter(response=None).earliest()
                event.response = self.process(event.recipient, event.request)
                event.save()

            # Check for thread stop
            if self.stopped():
                break

            # Update every 50ms
            time.sleep(0.05)

    def process(
        self, recipient: Dict[str, str], request: Dict[str, Any]
    ) -> Dict[str, Union[str, int]]:
        """Processes request to recipient, returns response."""

        # Get request parameters
        try:
            recipient_type = recipient["type"]
            recipient_name = recipient["name"]
        except KeyError as e:
            message = "Unable to get request parameters: {}".format(e)
            self.logger.exception(message)
            return {"status": 400, "message": message}

        # Process device requests
        if recipient_type == "Device":
            self.logger.debug("Processing device event request: {}".format(request))

            # Clear device response and send request to device
            # TODO: Put this lock into state and access dict via decorators
            with self.state.lock:
                self.state.device["response"] = None
                self.state.device["request"] = request

            # Wait for response
            start_time = time.time()
            while True:

                # Check for response
                response = self.state.device["response"]
                if response != None:
                    delta = time.time() - start_time
                    message = "Received response after {:.2F} seconds: {}".format(
                        delta, response
                    )
                    self.logger.debug(message)

                    # Verify response is valid
                    try:
                        status = response["status"]
                        message = response["message"]
                        return {"status": status, "message": message}
                    except KeyError as e:
                        message = "Received invalid response"
                        self.logger.exception(message)
                        return {"status": 500, "message": message}

                # Check for timeout
                if time.time() - start_time > self.timeout:
                    message = "Request timed out after {} seconds".format(self.timeout)
                    self.logger.critical(message)
                    resp = {"status": 500, "message": message}
                    self.logger.debug("Returning response: {}".format(resp))
                    return resp

                # Update every 50ms
                time.sleep(0.05)

        # Process peripheral requests
        elif recipient_type == "Peripheral":
            self.logger.debug("Processing peripheral event request: {}".format(request))

            # Check if recipient exists
            if recipient_name not in self.state.peripherals:
                message = "Unknown peripheral recipient `{}`".format(recipient_name)
                self.logger.debug(message)
                return {"status": 400, "message": message}

            # Clear peripheral response and send request to peripheral
            # TODO: Put this lock into state and access dict via decorators
            with self.state.lock:
                self.state.peripherals[recipient_name]["response"] = None
                self.state.peripherals[recipient_name]["request"] = request

            # Wait for response
            start_time = time.time()
            while True:

                # Check for response
                response = self.state.peripherals[recipient_name]["response"]
                if response != None:
                    self.logger.debug("Received response: {}".format(response))

                    # Verify response is valid
                    try:
                        status = response["status"]
                        message = response["message"]
                        return {"status": status, "message": message}
                    except KeyError as e:
                        message = "Received invalid response"
                        self.logger.exception(message)
                        return {"status": 500, "message": message}

                # Check for timeout
                if time.time() - start_time > self.timeout:
                    message = "Request timed out after {} seconds".format(self.timeout)
                    self.logger.critical(message)
                    return {"status": 500, "message": message}

                # Update every 50ms
                time.sleep(0.05)

        else:
            # Return response
            message = "Unable to process request for recipient: {}".format(recipient)
            self.logger.debug(message)
            return {"status": 400, "message": "Unknown recipient type"}
