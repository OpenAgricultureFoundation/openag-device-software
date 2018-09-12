# Import python modules
import copy
import glob
import json
import logging
import os
import shutil
import sys
import threading
import datetime
import time
import traceback
import ast
import socket

# Import device utilities
from device.utilities.accessors import get_nested_dict_safely


# Import the IoT communications class
from iot.iot_pubsub import IoTPubSub
from connect.connect_utils import ConnectUtils


class IoTManager:
    """Manages IoT communications to the Google cloud backend MQTT service."""

    # Initialize logger
    extra = {"console_name": "IoT", "file_name": "IoT"}
    logger = logging.getLogger("iot")
    logger = logging.LoggerAdapter(logger, extra)

    # Place holder for thread object.
    thread = None

    # Keep track of the previous values that we have published.
    # We only publish a value if it changes.
    prev_vars = None
    sentAboutJson = False
    last_status = datetime.datetime.utcnow()
    status_publish_freq_secs = 300

    #--------------------------------------------------------------------------
    def __init__(self, state, ref_device_manager):
        """ Class constructor """
        self.iot = None
        self.state = state
        self.error = None
        self.ref_device_manager = ref_device_manager
        # Initialize our state.  These are filled in by the IoTPubSub class
        self.state.iot = {
            "error": self.error,
            "connected": "No",
            "received_message_count": 0,
            "published_message_count": 0,
        }

        self._stop_event = threading.Event()  # so we can stop this thread
        self.reset()

    #--------------------------------------------------------------------------
    def reset(self):
        try:
            # pass in the callback that receives commands
            self.iot = IoTPubSub(self, self.command_received, self.state.iot)
        except (Exception) as e:
            self.iot = None
            self.error = str(e)
            # exc_type, exc_value, exc_traceback = sys.exc_info()
            self.logger.error("Couldn't create IoT connection: {}".format(e))
            # traceback.print_tb( exc_traceback, file=sys.stdout )

    #--------------------------------------------------------------------------
    def killIoTPubSub(self, msg):
        self.iot = None
        self.error = msg
        self.logger.error("Killing IoTPubSub: {}".format(msg))

    #--------------------------------------------------------------------------
    def command_received(self, command, arg0, arg1):
        """Process commands received from the backend (UI).
            This is a callback that is called by the IoTPubSub class when this
            device receives commands from the UI."""

        if None == self.iot:
            return

        try:
            if command == IoTPubSub.CMD_START:
                recipe_json = arg0
                recipe_dict = json.loads(arg0)

                # Make sure we have a valid recipe uuid
                if (
                    "uuid" not in recipe_dict
                    or None == recipe_dict["uuid"]
                    or 0 == len(recipe_dict["uuid"])
                ):
                    self.logger.error("command_received: missing recipe UUID")
                    return
                recipe_uuid = recipe_dict["uuid"]

                # first stop any recipe that may be running
                self.ref_device_manager.process_stop_recipe_event()

                # put this recipe in our DB (by uuid)
                self.ref_device_manager.load_recipe_json(recipe_json)

                # start this recipe from our DB (by uuid)
                self.ref_device_manager.process_start_recipe_event(recipe_uuid)

                # record that we processed this command
                self.iot.publishCommandReply(command, recipe_json)
                return

            if command == IoTPubSub.CMD_STOP:
                self.ref_device_manager.process_stop_recipe_event()
                self.iot.publishCommandReply(command, "")
                return

            self.logger.error("command_received: Unknown command: {}".format(command))
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.logger.critical("Exception in command_received(): %s" % e)
            traceback.print_tb(exc_traceback, file=sys.stdout)
            return False

    #--------------------------------------------------------------------------
    @property
    def error(self):
        """ Gets error value. """
        return self._error

    @error.setter
    def error(self, value):
        """ Safely updates recipe error in shared state. """
        self._error = value
        with threading.Lock():
            self.state.iot["error"] = value

    #--------------------------------------------------------------------------
    @property
    def connected(self):
        if self.iot is None:
            return False
        return self.iot.connected

    @connected.setter
    def connected(self, value):
        if self.iot is None:
            return
        self.iot.connected = value

    #--------------------------------------------------------------------------
    def publishMessage(name, msg_json):
        """ Send a command reply. """
        if self.iot is None:
            return
        self.iot.publishCommandReply(name, msg_json)

    #--------------------------------------------------------------------------
    def spawn(self):
        self.logger.info("Spawning IoT thread")
        self.thread = threading.Thread(target=self.thread_proc)
        self.thread.daemon = True
        self.thread.start()

    #--------------------------------------------------------------------------
    def stop(self):
        self.logger.info("Stopping IoT thread")
        self._stop_event.set()

    #--------------------------------------------------------------------------
    def stopped(self):
        return self._stop_event.is_set()

    #--------------------------------------------------------------------------
    def publish(self):
        if self.iot is None:
            return

        # Safely get vars dict
        vars_dict = get_nested_dict_safely(
            self.state.environment,
            ["reported_sensor_stats", "individual", "instantaneous"],
        )

        # Check if vars is empty, if so turn into a dict
        if vars_dict == None:
            vars_dict = {}

        # Keep a copy of the first set of values (usually None).
        if self.prev_vars is None:
            self.prev_vars = copy.deepcopy(vars_dict)

        # for each value, only publish the ones that have changed.
        for var in vars_dict:
            if self.prev_vars[var] != vars_dict[var]:
                self.prev_vars[var] = copy.deepcopy(vars_dict[var])
                self.iot.publishEnvVar(var, vars_dict[var])

    #--------------------------------------------------------------------------
    def get_IP(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
        except:
            pass
        IP = s.getsockname()[0]
        s.close()
        return IP

    #--------------------------------------------------------------------------
    def thread_proc(self):
        while True:

            # Make sure we have a valid registration + device id
            # export DEVICE_ID=EDU-BD9BC8B7-f4-5e-ab-3f-07-fd
            device_id = ConnectUtils.get_device_id_from_file()
            if device_id is None:
                time.sleep(15)
                self.logger.error("Missing device id file.")
                self.clean_up_images() # don't fill the disk!
                continue
            os.environ["DEVICE_ID"] = device_id

            # Re-connect to IoT if we lose it (or never had it to begin with)
            if self.iot is None:
                time.sleep(15)
                self.reset()
                continue

            # Publish a boot message
            if not self.sentAboutJson:
                self.sentAboutJson = True
                try:
                    # Get device config
                    device = None
                    if os.path.exists("config/device.txt"):
                        with open("config/device.txt") as f:
                            device = f.readline().strip()

                    about_dict = { 
                        "package_version": 
                            self.state.upgrade.get('current_version','unknown'),
                        "device_config": device, 
                        "IP": self.get_IP() }
                    about_json = json.dumps(about_dict)
                    self.iot.publishCommandReply("boot", about_json)

                except:
                    self._error = "Unable to send boot message."
                    self.logger.critical(self._error)

            # Publish status every 5 minutes
            secs_since_last_status = (
                datetime.datetime.utcnow() - self.last_status
            ).seconds
            if secs_since_last_status > self.status_publish_freq_secs:
                try:
                    self.last_status = datetime.datetime.utcnow()
                    status_dict = {}
                    status_dict["timestamp"] = \
                        time.strftime("%FT%XZ", time.gmtime())
                    status_dict["IP"] = self.get_IP()

                    # get the current version from the upgrade state
                    status_dict["package_version"] = \
                        self.state.upgrade.get('current_version','unknown')

                    device = None
                    if os.path.exists("config/device.txt"):
                        with open("config/device.txt") as f:
                            device = f.readline().strip()
                    status_dict["device_config"] = device

                    status_dict["status"] = self.state.resource.get("status",'')
                    status_dict["internet_connection"] = \
                        self.state.resource["internet_connection"]
                    status_dict["memory_available"] = \
                        self.state.resource["free_memory"]
                    status_dict["disk_available"] = \
                        self.state.resource["available_disk_space"]

                    status_dict["iot_status"] = self.state.iot["connected"]
                    status_dict["iot_received_message_count"] = self.state.iot[
                        "received_message_count"
                    ]
                    status_dict["iot_published_message_count"] = self.state.iot[
                        "published_message_count"
                    ]

                    status_dict["recipe_percent_complete"] = self.state.recipe[
                        "percent_complete"
                    ]
                    status_dict["recipe_percent_complete_string"] = self.state.recipe[
                        "percent_complete_string"
                    ]
                    status_dict["recipe_time_remaining_minutes"] = self.state.recipe[
                        "time_remaining_minutes"
                    ]
                    status_dict["recipe_time_remaining_string"] = self.state.recipe[
                        "time_remaining_string"
                    ]
                    status_dict["recipe_time_elapsed_string"] = self.state.recipe[
                        "time_elapsed_string"
                    ]

                    status_json = json.dumps(status_dict)
                    self.iot.publishCommandReply("status", status_json)
                except:
                    self._error = "Unable to send status message."
                    self.logger.critical(self._error)

            if self.stopped():
                break

            # send and receive messages over IoT
            try:
                self.iot.process_network_events()
            except:
                pass

            # check for images to publish
            try:
                image_file_list = glob.glob("images/*.png")
                for image_file in image_file_list:

                    # Is this file open by a process? (fswebcam)
                    if (
                        0
                        == os.system(
                            "lsof -f -- {} > /dev/null 2>&1".format(image_file)
                        )
                    ):
                        continue  # Yes, so skip it and try the next one.

                    # 2018-06-15-T18:34:45Z_Camera-Top.png
                    fn1 = image_file.split("_")
                    fn2 = fn1[1]  # Camera-Top.png
                    fn3 = fn2.split(".")
                    camera_name = fn3[0]  # Camera-Top

                    # get the file contents
                    f = open(image_file, "rb")
                    file_bytes = f.read()
                    f.close()

                    # if the size is < 40KB, then it is garbage we delete
                    if len(file_bytes) < 40000:
                        os.remove(image_file)
                        continue

                    self.iot.publishBinaryImage(camera_name, "png", file_bytes)

                    # Check if stored directory exists, if not create it
                    if not os.path.isdir("images/stored"):
                        os.mkdir("images/stored")

                    # Move image from /images once processed
                    stored_image_file = image_file.replace("images", "images/stored")
                    shutil.move(image_file, stored_image_file)

                    # TODO: Check for external storage device for images
                    # Need to think through how this will interact with
                    # on-device UI image display...how does find images

            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                self.logger.critical("Exception: {}".format(e))
                traceback.print_tb(exc_traceback, file=sys.stdout)

            # idle for a bit
            time.sleep(1)

    #--------------------------------------------------------------------------
    def clean_up_images(self):
        """ If we are not registered for a long time, the camera peripheral
            will still be taking pictures every hour by default.  So to avoid
            filling up the small disk, we remove any images that build up.
        """
        try:
            image_file_list = glob.glob("images/*.png")
            for image_file in image_file_list:
                # Is this file open by a process? (fswebcam)
                if ( 0 == os.system(
                        "lsof -f -- {} > /dev/null 2>&1".format(image_file)
                    )
                ):
                    continue  # Yes, so skip it and try the next one.
                os.remove(image_file)
        except Exception as e:
            self.logger.error("clean_up_images: {}".format(e))
