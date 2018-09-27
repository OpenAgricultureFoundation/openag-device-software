# Import standard python modules
import logging, threading, time, platform

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.statemachine.manager import StateMachineManager

# Import manager elements
from device.connect.utilities import ConnectUtilities


class ConnectManager:
    """ Sets up and manages internet and IoT connections. """

    # Place holder for thread object.
    thread = None

    def __init__(self, state, ref_iot_manager):
        """Initializes connect manager."""

        # Initialize logger
        self.logger = Logger("ConnectManager", __name__)
        self.logger.debug("Initializing manager")

        # Initialize our state
        self.state = state
        self.error = None
        self.status = "Initializing..."
        self.ref_iot_manager = ref_iot_manager
        self.update()
        self._stop_event = threading.Event()  # so we can stop this thread

        # this never changes, so only get once
        self.state.connect["is_bbb"] = ConnectUtilities.is_bbb()

        # initialize this
        self.state.connect["device_UI"] = ConnectUtilities.get_remote_UI_URL()

    @property
    def error(self):
        """ Gets error value. """
        return self._error

    @error.setter
    def error(self, value):
        """ Safely updates shared state. """
        self._error = value
        with threading.Lock():
            self.state.connect["error"] = value

    @property
    def status(self):
        """ Gets status value. """
        return self._status

    @status.setter
    def status(self, value):
        """ Safely updates shared state. """
        self._status = value
        with self.state.lock:
            self.state.connect["status"] = value

    def spawn(self):
        self.logger.info("Spawning connect manager thread")
        self.thread = threading.Thread(target=self.thread_proc)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.logger.info("Stopping connect manager thread")
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def thread_proc(self):
        while True:
            if self.stopped():
                break
            self.update()
            if ConnectUtilities.valid_internet_connection():
                time.sleep(300)  # idle for 5 min
            else:
                time.sleep(5)  # fast idle until we get connected

    def update(self):
        # these may change, so get new values every loop
        self.state.connect[
            "valid_internet_connection"
        ] = ConnectUtilities.valid_internet_connection()
        self.state.connect["is_wifi_bbb"] = ConnectUtilities.is_wifi_bbb()
        self.state.connect["wifis"] = ConnectUtilities.get_wifis()
        self.state.connect["IP"] = ConnectUtilities.get_IP()
        self.state.connect[
            "is_registered_with_IoT"
        ] = ConnectUtilities.is_registered_with_IoT()
        self.state.connect["device_id"] = ConnectUtilities.get_device_id()
        self.state.connect["iot_connection"] = self.state.iot[
            "connected"
        ]  # the IoTManager already does this

        if ConnectUtilities.valid_internet_connection():
            self.status = "Connected"
        else:
            self.status = "Not Connected"
