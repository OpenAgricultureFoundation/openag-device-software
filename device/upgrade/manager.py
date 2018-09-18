# Import python modules
import logging
import threading
import time
import platform
from device.upgrade.utilities import UpgradeUtilities


class UpgradeManager:
    """ Manage software upgrades. """

    # Initialize logger
    extra = {"console_name": "UpgradeManager", "file_name": "upgrade"}
    logger = logging.getLogger("upgrade")
    logger = logging.LoggerAdapter(logger, extra)

    # Place holder for thread object.
    thread = None

    # ------------------------------------------------------------------------
    def __init__(self, state):
        """ Class constructor """
        # Initialize our state
        self.state = state
        UpgradeUtilities.save_state(state)
        self.error = None
        stat = "Initializing..."
        self.status = stat
        self.state.upgrade["current_version"] = stat
        self.state.upgrade["upgrade_version"] = stat
        self.state.upgrade["show_upgrade"] = False
        self._stop_event = threading.Event()  # so we can stop this thread

    # ------------------------------------------------------------------------
    @property
    def error(self):
        """ Gets error value. """
        return self._error

    @error.setter
    def error(self, value):
        """ Safely updates shared state. """
        self._error = value
        with threading.Lock():
            self.state.upgrade["error"] = value

    # ------------------------------------------------------------------------
    @property
    def status(self):
        """ Gets status value. """
        return self.state.upgrade["status"]

    @status.setter
    def status(self, value):
        """ Safely updates shared state. """
        with threading.Lock():
            self.state.upgrade["status"] = value

    # ------------------------------------------------------------------------
    def spawn(self):
        self.logger.info("Spawning upgrade manager thread")
        self.thread = threading.Thread(target=self.thread_proc)
        self.thread.daemon = True
        self.thread.start()

    # ------------------------------------------------------------------------
    def stop(self):
        self.logger.info("Stopping upgrade manager thread")
        self._stop_event.set()

    # ------------------------------------------------------------------------
    def stopped(self):
        return self._stop_event.is_set()

    # ------------------------------------------------------------------------
    def thread_proc(self):
        while True:
            if self.stopped():
                break
            time.sleep(30)  # allow time to start the django UI
            self.update()
            time.sleep(86400)  # idle for one day

    # ------------------------------------------------------------------------
    def update(self):
        self.logger.info("Checking for software update")
        UpgradeUtilities.update_dict()
