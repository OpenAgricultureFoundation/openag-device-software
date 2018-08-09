# Import python modules
import logging
import subprocess
import threading
import time
import socket
import json
import os
import platform


class ConnectManager:
    """ Sets up and manages internet and IoT connections. """

    # Initialize logger
    extra = {"console_name": "ConnectManager", "file_name": "connect"}
    logger = logging.getLogger("connect")
    logger = logging.LoggerAdapter(logger, extra)

    # Place holder for thread object.
    thread = None

    # ------------------------------------------------------------------------
    def __init__(self, state, ref_iot_manager, ref_resource_manager):
        """ Class constructor """
        # Initialize our state
        self.state = state
        self.error = None
        self.status = 'OK'
        self.ref_iot_manager = ref_iot_manager
        self.ref_resource_manager = ref_resource_manager
        self.update()
        self._stop_event = threading.Event()  # so we can stop this thread

        # these values never change, so only get them once
        self.state.connect["is_bbb"] = self.is_bbb()
        self.state.connect["is_wifi_bbb"] = self.is_wifi_bbb()
        self.state.connect["device_UI"] = self.get_remote_UI_URL()

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
            self.state.connect["error"] = value

    # ------------------------------------------------------------------------
    @property
    def status(self):
        """ Gets status value. """
        return self._status

    @status.setter
    def status(self, value):
        """ Safely updates shared state. """
        self._status = value
        with threading.Lock():
            self.state.connect["status"] = value

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
    def thread_proc(self):
        while True:
            if self.stopped():
                break

            self.update()

            if self.ref_resource_manager.connected:
                time.sleep(300)  # idle for 5 min
            else:
                time.sleep(5)  # fast idle until we get connected

    # ------------------------------------------------------------------------
    def update(self):
        # these may change, so get new values every loop
        self.state.connect["valid_internet_connection"] = \
            self.ref_resource_manager.connected
        self.state.connect["wifis"] = self.get_wifis()
        self.state.connect["IP"] = self.get_IP()
        self.state.connect["is_registered_with_IoT"] = \
            self.is_registered_with_IoT()
        self.state.connect["device_id"] = \
            self.get_device_id()
        self.state.connect["iot_connection"] = \
            self.state.iot["connected"]  # the IoTManager already does this
#debugrob, delete this
        if platform.node() == 'rbaynes.local':
            self.state.connect["valid_internet_connection"] = False

    # ------------------------------------------------------------------------
    # Returns True if this is a Beaglebone.
    def is_bbb(self):
        # Only for rob developing
        if platform.node() == 'rbaynes.local':
            return True

        try:
            # command and list of args as list of string
            cmd = ["cat", "/etc/dogtag"]
            with subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) as proc1:
                output = proc1.stdout.read().decode("utf-8")
                output += proc1.stderr.read().decode("utf-8")
                if 'Beagle' in output:
                    return True
        except:
            pass
        return False

    # ------------------------------------------------------------------------
    # Return the list of local wifis.
    def get_wifis(self):
        # Only for rob developing
        if platform.node() == 'rbaynes.local':
            return ['wifi1', 'wifi2', 'MIT']

#debugrob, implement this
        wifis = ['debugrob']
        return wifis

    # ------------------------------------------------------------------------
    # Returns True if this BBB is a wifi model.
    def is_wifi_bbb(self):
        # Only for rob developing
        if platform.node() == 'rbaynes.local':
            return True

        if not self.is_bbb():
            return False
        try:
            # command and list of args as list of string
            cmd = ["ifconfig", "wlan0"]
            with subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) as proc1:
                output = proc1.stdout.read().decode("utf-8")
                output += proc1.stderr.read().decode("utf-8")
                if 'wlan0: flags' in output:
                    return True
        except:
            pass
        return False

    # ------------------------------------------------------------------------
    def get_IP(self):
        """ Returns the IP address of the active interface. """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except:
            pass
        return 'No IP address'

    # ------------------------------------------------------------------------
    def get_remote_UI_URL(self):
        """ Return the URL to the device UI. """
        try:
            about = json.load(open("about.json"))
            sn = str(about["serial_number"])
            sn = sn.replace('-', '.')
            return "http://{}.serveo.net/".format(sn)
        except:
            pass
        return ''

    # ------------------------------------------------------------------------
    def is_registered_with_IoT(self):
        """ Returns True if there is a valid IoT registration. """
        if os.path.exists('registration/data/device_id.bash') and \
                os.path.exists('registration/data/roots.pem') and \
                os.path.exists('registration/data/rsa_cert.pem') and \
                os.path.exists('registration/data/rsa_private.pem'):
            return True
        return False

    # ------------------------------------------------------------------------
    def get_device_id(self):
        """ Returns the device ID string. """
        if not self.is_registered_with_IoT():
            return ''
        try:
            f = open('registration/data/device_id.bash')
            contents = f.read()
            index = contents.find('=')
            devid = contents[index + 1:]
            return devid.rstrip()
        except:
            pass
        return ''





