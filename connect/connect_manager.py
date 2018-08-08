# Import python modules
import glob
import logging
import os
import subprocess
import sys
import threading
import time
import urllib.request

from app.models import EnvironmentModel
from app.models import EventModel

class ConnectManager:
    """ Sets up and manages internet and IoT connections. """

    # Initialize logger
    extra = {"console_name": "ConnectManager", "file_name": "connect"}
    logger = logging.getLogger("connect")
    logger = logging.LoggerAdapter(logger, extra)

    # Place holder for thread object.
    thread = None

    # ------------------------------------------------------------------------
    def __init__(self, state, ref_iot_manager):
        """ Class constructor """
        # Initialize our state
        self.state = state
        self.connected = False
        self.error = None
        self.status = 'OK'
        self.ref_iot_manager = ref_iot_manager
        self.update()
        self._stop_event = threading.Event()  # so we can stop this thread

    # ------------------------------------------------------------------------
    @property
    def error(self):
        """ Gets error value. """
        return self._error

    @error.setter
    def error(self, value):
        """ Safely updates recipe error in shared state. """
        self._error = value
        with threading.Lock():
            self.state.connect["error"] = value

    # ------------------------------------------------------------------------
    @property
    def status(self):
        """ Gets status value. """
        return self._status

    @status.setter
    def status(self, value):
        """ Safely updates recipe status in shared state. """
        self._status = value
        with threading.Lock():
            self.state.connect["status"] = value

    # ------------------------------------------------------------------------
    @property
    def connected(self):
        return self._connected

    @connected.setter
    def connected(self, value):
        self._connected = value

    # ------------------------------------------------------------------------
    def spawn(self):
        self.logger.info("Spawning connect manager thread")
        self.thread = threading.Thread(target=self.thread_proc)
        self.thread.daemon = True
        self.thread.start()

    # ------------------------------------------------------------------------
    def stop(self):
        self.logger.info("Stopping connect manager thread")
        self._stop_event.set()

    # ------------------------------------------------------------------------
    def stopped(self):
        return self._stop_event.is_set()

    # ------------------------------------------------------------------------
    def update(self):
#debugrob, check internet and IoT status here
        self.logger.debug("debugrob")

    # ------------------------------------------------------------------------
    def valid_internet_connection(self):
        ret = False
        try:
            urllib.request.urlopen("http://google.com")
            ret = True
        except:
            ret = False
        return ret

    # ------------------------------------------------------------------------
    def thread_proc(self):
        disconnected = True
        while True:
            if self.stopped():
                break

#debugrob, do reset/etc in response to user button click.
            if self.valid_internet_connection():
                self.connected = True
                if disconnected:
                    self.ref_iot_manager.reset()
                    disconnected = False
            else:
                self.connected = False
                disconnected = True

            self.update()

            if self.connected:
                time.sleep(60)  # idle 1 min
            else:
                time.sleep(1)  # fast idle until we get connected




