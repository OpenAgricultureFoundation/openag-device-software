# Import python modules
import os, sys, glob, logging, subprocess, threading, time, urllib.request

# Import python types
from typing import Dict, List

# Import django modules
from django.db import connection  # so we can do raw sql queries

# Import app models
from app.models import EnvironmentModel, EventModel

# Import device utilities
from device.utilities import logger, accessors, constants
from device.utilities.statemachine import manager, modes
from device.utilities.state.main import State

# Import device managers
from device.iot.manager import IoTManager
from device.connect import utilities as connect_utilities

# Initialize file paths
IMAGES_PATH = "data/images/*.png"
STORED_IMAGES_PATH = "data/images/stored/*.png"
LOGS_PATH = "data/logs/"
PERIPHERAL_LOGS_PATH = "data/logs/peripherals/"
SYSTEM_LOGS_PATH = "/var/log/"

# TODO Notes:
# Remove redundant functions accross connect, iot, update, resource, and upgrade
# We may just want many of these functions in the manager or in device utilities
# Adjust function and variable names to match python conventions
# Add static type checking
# Write tests
# Catch specific exceptions
# Pull out file path strings to top of file
# Inherit from state machine manager
# Always use get method to access dicts unless checking for KeyError (rare cases)
# Always use decorators to access shared state w/state.lock
# Use consistent names for class variables and state variables
# Always logger class from device utilities
# Make logic easy to read (descriptive variables, frequent comments, minimized nesting)


class ResourceManager(manager.StateMachineManager):
    """Manages critical resources: disk space and database capacity."""

    # Initialize connection status
    _connected: bool = False
    reconnected: bool = False

    def __init__(self, state: State, iot: IoTManager) -> None:
        """Initializes manager."""

        # Initialize parent class
        super().__init__()

        # Initialize parameters
        self.state = state
        self.iot = iot

        # TODO: Remove this
        self.error = "None"

        # Initialize logger
        self.logger = logger.Logger("Resource", "resource")
        self.logger.debug("Initializing manager")

        # Initialize state machine transitions
        self.transitions: Dict[str, List[str]] = {
            modes.NORMAL: [modes.SHUTDOWN, modes.ERROR],
            modes.ERROR: [modes.SHUTDOWN],
        }

        # Initialize state machine mode
        self.mode = modes.NORMAL

    @property
    def connected(self) -> bool:
        """Gets connection status."""
        return self._connected

    @connected.setter
    def connected(self, value: bool) -> None:
        """Sets connection status, updates reconnection status, and logs changes."""

        # Set previous and current connection state
        prev_connected = self._connected
        self._connected = value

        # Check for new connection
        if prev_connected != self._connected and self._connected:
            self.logger.info("Connected to internet")
            self.reconnected = True

        # Check for new disconnection
        elif prev_connected != self._connected and not self._connected:
            self.logger.info("Disconnected from internet")
            self.reconnected = False

        # No change to connection
        else:
            self.reconnected = False

        # Update connection status in shared state
        with self.state.lock:
            self.state.resource["internet_connection"] = value

    @property
    def status(self) -> str:
        """Gets status value."""
        return self.state.resource.get("status")  # type: ignore

    @status.setter
    def status(self, value: str) -> None:
        """Safely updates status in shared state."""
        with self.state.lock:
            self.state.resource["status"] = value

    @property
    def error(self) -> str:
        """Gets error value."""
        return self.state.resource.get("error")  # type: ignore

    @error.setter
    def error(self, value: str) -> None:
        """Safely updates error in shared state."""
        with self.state.lock:
            self.state.resource["error"] = value

    @property
    def free_disk(self) -> str:
        """Gets free disk value."""
        # TODO: Fix name
        return self.state.resource.get("available_disk_space")  # type: ignore

    @free_disk.setter
    def free_disk(self, value: str) -> None:
        """Safely updates free disk in shared state."""
        with self.state.lock:
            # TODO: Fix name
            self.state.resource["available_disk_space"] = value

    @property
    def free_memory(self) -> str:
        """Gets free memory value."""
        return self.state.resource.get("free_memory")  # type: ignore

    @free_memory.setter
    def free_memory(self, value: str) -> None:
        """Safely updates free memory in shared state."""
        with self.state.lock:
            self.state.resource["free_memory"] = value

    @property
    def database_size(self) -> str:
        """Gets database size value."""
        return self.state.resource.get("database_size")  # type: ignore

    @database_size.setter
    def database_size(self, value: str) -> None:
        """Safely updates database size in shared state."""
        with self.state.lock:
            self.state.resource["database_size"] = value

    ##### STATE MACHINE FUNCTIONS ######################################################

    def run(self) -> None:
        """Runs state machine."""

        # Loop forever
        while True:

            # Check if manager is shutdown
            if self.is_shutdown:
                break  # TODO: Fix name

            # Check for mode transitions
            if self.mode == modes.NORMAL:
                self.run_normal_mode()
            elif self.mode == modes.ERROR:
                self.run_error_mode()  # defined in parent classs
            elif self.mode == modes.SHUTDOWN:
                self.run_shutdown_mode()  # defined in parent class
            else:
                self.logger.critical("Invalid state machine mode")
                self.mode = modes.INVALID
                self.is_shutdown = True
                break

    def run_normal_mode(self) -> None:
        """Runs normal mode."""

        # Initialize last update time
        last_update_time = 0.0

        # Loop forever
        while True:

            # Set resource update interval
            if not self.connected:
                update_interval = 5  # seconds
            else:
                update_interval = 300  # seconds -> 5 minutes

            # Update connection and storage state every update interval
            if time.time() - last_update_time > update_interval:
                last_update_time = time.time()
                self.update_connection()
                self.update_storage()

            # Check for events
            self.check_events()

            # Check for transitions
            if self.new_transition(modes.NORMAL):
                break

            # Update every 100ms
            time.sleep(0.1)

    ##### HELPER FUNCTIONS #############################################################

    def update_connection(self) -> None:
        """Updates connection information."""
        self.logger.debug("Updating connection")

        # Update connection status
        self.connected = connect_utilities.valid_internet_connection()

        # Reset iot manager on reconnect event
        if self.reconnected:
            self.iot.reset()  # type: ignore

    def update_storage(self) -> None:
        """Updates storage information."""
        self.logger.debug("Updating storage")

        # Get storage information and update in shared state
        self.free_disk = self.get_free_disk()
        self.free_memory = self.get_free_memory()
        self.database_size = self.get_database_size()

        # Convert num strings to float
        free_disk = accessors.floatify_string(self.free_disk)
        free_memory = accessors.floatify_string(self.free_disk)

        # Check for low disk space (<50MB)
        if free_disk < 50.0 * constants.MEGABYTE:
            self.logger.warning("Low disk, remaining: {}".format(self.free_disk))
            low_disk = True
        else:
            low_disk = False

        # Check for low memory (<10MB)
        if free_memory < 10.0 * constants.MEGABYTE:
            self.logger.warning("Low memory, remaining: {}".format(self.free_memory))
            low_memory = True
        else:
            low_memory = False

        # Update status and notify cloud system if either resource is low
        if low_disk or low_memory:
            self.status = "Low resources, disk: {}, memory: {}".format(
                self.free_disk, self.free_memory
            )
            self.iot.publish_message("alert", self.status)  # type: ignore
        else:
            self.status = "OK"

        # Clear disk if low
        if low_disk:
            self.clean_up_disk()
            self.clean_up_database(keep=50)

    def get_free_disk(self) -> str:
        """Returns the amount of free disk space on Debian and OSX."""
        self.logger.debug("Getting free disk")

        # Build linux commands
        command1 = ["df", "-h", "/"]
        command2 = ["awk", "{print $4}"]
        command3 = ["tail", "-1"]

        # Tweak commands for OSX
        if sys.platform == "darwin":
            command1 = ["df", "-hg", "/"]  # show in G without chars

        # Get free disk
        try:
            with subprocess.Popen(command1, stdout=subprocess.PIPE) as process1:
                with subprocess.Popen(
                    command2, stdin=process1.stdout, stdout=subprocess.PIPE
                ) as process2:
                    with subprocess.Popen(
                        command3, stdin=process2.stdout, stdout=subprocess.PIPE
                    ) as process3:
                        free_disk = process3.stdout.read().decode("utf-8").rstrip()
        except Exception:
            self.logger.exception("Unable to get free disk, unhandled exception")
            return "Unknown"

        # Tweak response from OSX
        if sys.platform == "darwin":
            free_disk += "G"  # for OSX, add on 'G' like Linux

        # Successfully got free disk space
        self.logger.debug("Free disk: {}".format(free_disk))
        return free_disk

    def get_free_memory(self) -> str:
        """Return a string showing the amount of free RAM in Megabytes on 
        Debian/Linux and OSX."""
        self.logger.debug("Getting free memory")

        # Build linux commands
        command1 = ["free", "-ht"]
        command2 = ["awk", "{print $4}"]
        command3 = ["tail", "-1"]

        # Tweak commands for OSX
        if sys.platform == "darwin":
            command1 = ["top", "-l", "1", "-s", "0"]
            command2 = ["grep", "PhysMem"]
            command3 = ["awk", "{print $6}"]

        # Execute commands
        try:
            with subprocess.Popen(command1, stdout=subprocess.PIPE) as process1:
                with subprocess.Popen(
                    command2, stdin=process1.stdout, stdout=subprocess.PIPE
                ) as process2:
                    with subprocess.Popen(
                        command3, stdin=process2.stdout, stdout=subprocess.PIPE
                    ) as process3:
                        free_memory = process3.stdout.read().decode("utf-8").rstrip()
        except Exception as e:
            self.logger.exception("Unable to get free memory, unhandled exception")
            return "Unknown"

        # Successfully got free memory
        self.logger.debug("Free memory: {}".format(free_memory))
        return free_memory

    def get_database_size(self) -> str:
        """Gets database size as a string."""
        self.logger.debug("Getting database size")

        # Build query
        query = "select pg_size_pretty(pg_database_size('openag_brain'));"

        # Execute query
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                database_size = result[0]
        except Exception:
            self.logger.exception("Unable to get database size, unhandled exception")
            return "Unknown"

        # Successfully got database size
        self.logger.debug("Database size: {}".format(database_size))
        return database_size

    def clean_up_disk(self) -> None:
        """Cleans up disk by deleting all logs and old images."""
        self.logger.debug("Cleaning up disk")
        self.delete_files(IMAGES_PATH, keep=10)
        self.delete_files(STORED_IMAGES_PATH, keep=10)
        self.delete_files(SYSTEM_LOGS_PATH + "*.1")
        self.delete_files(LOGS_PATH + "*.1")
        self.delete_files(PERIPHERAL_LOGS_PATH + "*.1")

    def delete_files(self, path: str, keep: int = 0) -> None:
        """Deletes files in path with the option to keep specified number of files.
        Assumes files for keeping are named with timestamps."""
        self.logger.info("Deleting files in: {}, keeping: {}".format(path, keep))

        # TODO: Use file creation date metadata for determining oldest files

        # Get filepaths and sort by name
        filepaths = glob.glob(path)
        filepaths.sort()

        # Get number of files in path
        num_files = len(filepaths)

        # Check for too many files
        if num_files > keep:

            # Delete oldest files
            index = num_files - keep
            old_filepaths = filepaths[:index]
            for filepath in old_filepaths:
                os.system("rm -f {}".format(filepath))

    def clean_up_database(self, keep: int = 0) -> None:
        """Cleans up database, deletes old entries from event and environment tables."""
        self.logger.info("Cleaning up database")

        # Get number of event entries
        events = EventModel.objects.all()
        num_event_entries = len(events)

        # Check for too many event entries
        if num_event_entries > keep:

            # Delete oldest event entries
            index = num_event_entries - keep
            old_events = EventModel.objects.order_by("timestamp")[:index]
            for event in old_events:
                event.delete()

        # Get number of environment entries
        environments = EnvironmentModel.objects.all()
        num_environment_entries = len(environments)

        # Check for too many environment entries
        if num_environment_entries > keep:

            # Delete oldest environment entries
            index = num_environment_entries - keep
            old_environments = EnvironmentModel.objects.order_by("timestamp")[:index]
            for environment in old_environments:
                environment.delete()


################################## LEGACY ##############################################


# # Import python modules
# import os, sys, glob, logging, subprocess, threading, time, urllib.request

# # Import django modules
# from django.db import connection  # so we can do raw sql queries

# # Import app models
# from app.models import EnvironmentModel
# from app.models import EventModel

# IMAGE_DIR = "data/images/"
# SYS_LOGS_DIR = "/var/log/"
# LOGS_DIR = "data/logs/"
# LOGSP_DIR = "data/logs/peripherals/"


# class ResourceManager:
#     """Manages critical resources: disk space and database capacity."""

#     # Initialize logger
#     extra = {"console_name": "ResourceManager", "file_name": "resource"}
#     logger = logging.getLogger("resource")
#     logger = logging.LoggerAdapter(logger, extra)

#     # Place holder for thread object.
#     thread = None

#     def __init__(self, state, ref_device_manager, ref_iot_manager):
#         """Initializes manager."""
#         self.logger.debug("Initializing manager")

#         # Initialize state
#         self.state = state
#         self.connected = False
#         self.error = None
#         self.ref_device_manager = ref_device_manager
#         self.ref_iot_manager = ref_iot_manager
#         self.update()
#         self._stop_event = threading.Event()  # so we can stop this thread

#     @property
#     def error(self):
#         """ Gets error value. """
#         return self._error

#     @error.setter
#     def error(self, value):
#         """ Safely updates recipe error in shared state. """
#         self._error = value
#         with threading.Lock():
#             self.state.resource["error"] = value

#     @property
#     def status(self):
#         """ Gets status value. """
#         return self._status

#     @status.setter
#     def status(self, value):
#         """ Safely updates recipe status in shared state. """
#         self._status = value
#         with threading.Lock():
#             self.state.resource["status"] = value

#     @property
#     def connected(self):
#         return self._connected

#     @connected.setter
#     def connected(self, value):
#         self._connected = value

#     def spawn(self):
#         self.logger.info("Spawning resource manager thread")
#         self.thread = threading.Thread(target=self.thread_proc)
#         self.thread.daemon = True
#         self.thread.start()

#     def stop(self):
#         self.logger.info("Stopping resource manager thread")
#         self._stop_event.set()

#     def stopped(self):
#         return self._stop_event.is_set()

#     def get_available_disk_space(self):
#         """
#         Return the amount of free disk space on Debian and OSX.
#         """
#         available_disk_space = "Unknown"
#         try:
#             # command and list of args as list of string
#             cmd1 = ["df", "-h", "/"]
#             cmd2 = ["awk", "{print $4}"]
#             cmd3 = ["tail", "-1"]

#             if sys.platform == "darwin":
#                 cmd1 = ["df", "-hg", "/"]  # for OSX, show in G without chars

#             with subprocess.Popen(cmd1, stdout=subprocess.PIPE) as proc1:

#                 with subprocess.Popen(
#                     cmd2, stdin=proc1.stdout, stdout=subprocess.PIPE
#                 ) as proc2:

#                     with subprocess.Popen(
#                         cmd3, stdin=proc2.stdout, stdout=subprocess.PIPE
#                     ) as proc3:
#                         available_disk_space = (
#                             proc3.stdout.read().decode("utf-8").rstrip()
#                         )

#             if sys.platform == "darwin":
#                 available_disk_space += "G"  # for OSX, add on 'G' like Linux

#         except Exception as e:
#             available_disk_space = e

#         return available_disk_space

#     def get_free_memory(self):
#         """
#         Return a string showing the amount of free RAM in 'M'egabytes on
#         Debian/Linux and OSX.
#         """
#         free_memory = "Unknown"
#         try:
#             # Linux commands
#             cmd1 = ["free", "-ht"]
#             cmd2 = ["awk", "{print $4}"]
#             cmd3 = ["tail", "-1"]

#             if sys.platform == "darwin":
#                 # OSX commands
#                 cmd1 = ["top", "-l", "1", "-s", "0"]
#                 cmd2 = ["grep", "PhysMem"]
#                 cmd3 = ["awk", "{print $6}"]

#             with subprocess.Popen(cmd1, stdout=subprocess.PIPE) as proc1:

#                 with subprocess.Popen(
#                     cmd2, stdin=proc1.stdout, stdout=subprocess.PIPE
#                 ) as proc2:

#                     with subprocess.Popen(
#                         cmd3, stdin=proc2.stdout, stdout=subprocess.PIPE
#                     ) as proc3:
#                         free_memory = proc3.stdout.read().decode("utf-8").rstrip()

#         except:
#             free_memory = "Unknown"

#         return free_memory

#     def delete_files(self, path, leave_newest=False):
#         try:
#             self.logger.info("Deleting all files in: " + path)
#             imageFileList = glob.glob(path)
#             imageFileList.sort()
#             """ If we want to keep the newest 10 files, then make the list
#                 contain everything but the last 10 (if there are more than 10).
#             """
#             if leave_newest and len(imageFileList) > 10:
#                 imageFileList = imageFileList[:len(imageFileList) - 10]
#             for imageFile in imageFileList:
#                 os.system("rm -f {}".format(imageFile))
#         except Exception as e:
#             self.logger.error(e)

#     def clean_up_disk(self):
#         """Delete most image and log files."""
#         self.delete_files(IMAGE_DIR + "*.png")
#         self.delete_files(IMAGE_DIR + "stored/*.png", leave_newest=True)
#         self.delete_files(SYS_LOGS_DIR + "*.1")
#         self.delete_files(LOGS_DIR + "*.1")
#         self.delete_files(LOGSP_DIR + "*.1")

#     def clean_up_database(self):
#         """Delete all but the most recent 50 events and
#            environments from database."""
#         try:
#             self.logger.info("Cleaning up database.")
#             # clean out the events
#             qs = EventModel.objects.all()  # query set of all items
#             eventCount = len(qs)
#             if 50 < eventCount:
#                 # delete oldest items ordered by timestamp, leaving at most 50
#                 deleteUpToIndex = eventCount - 50
#                 oldest = EventModel.objects.order_by("timestamp")[:deleteUpToIndex]
#                 for obj in oldest:
#                     obj.delete()

#             # clean out the environments
#             qs = EnvironmentModel.objects.all()  # query set of all items
#             eventCount = len(qs)
#             if 50 < eventCount:
#                 # delete oldest items ordered by timestamp, leaving at most 50
#                 deleteUpToIndex = eventCount - 50
#                 oldest = EnvironmentModel.objects.order_by("timestamp")[
#                     :deleteUpToIndex
#                 ]
#                 for obj in oldest:
#                     obj.delete()

#         except Exception as e:
#             self.logger.error(e)

#     def get_database_size(self):
#         ret = ""
#         # must use single quotes within the sql query, not double.
#         sql = "select pg_size_pretty( pg_database_size('openag_brain'));"
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute(sql)
#                 res = cursor.fetchone()
#                 ret = res[0]
#         except Exception as e:
#             self.logger.error(e)
#             ret = ""
#         return ret

#     def update(self):
#         free_disk = self.get_available_disk_space()
#         free_memory = self.get_free_memory()
#         database_size = self.get_database_size()

#         self.state.resource["available_disk_space"] = free_disk
#         self.state.resource["free_memory"] = free_memory
#         self.state.resource["database_size"] = database_size
#         self.state.resource["internet_connection"] = str(self.connected)

#         fd_units = free_disk[-1]  # last char is units: K/M/G
#         fm_units = free_memory[-1]  # last char is units: K/M/G

#         fd_val = free_disk[0:-1]
#         fm_val = free_memory[0:-1]
#         self.logger.debug(
#             "\n{}, {}, {}, {}".format(
#                 "free disk={}".format(free_disk),
#                 "free memory={}".format(free_memory),
#                 "DB size={}".format(database_size),
#                 "internet connection={}".format(self.connected),
#             )
#         )

#         # detect low memory and disk space
#         low_resources = False
#         low_disk = False
#         if "K" == fm_units or ("M" == fm_units and 10 >= float(fm_val)):
#             # 10M low memory limit
#             self.status = "Warning: low memory: {}".format(free_memory)
#             self.logger.warning(self.status)
#             low_resources = True

#         if "K" == fd_units or ("M" == fd_units and 50 >= float(fd_val)):
#             # 50M low disk limit
#             self.status = "Warning: low disk space: {}".format(free_disk)
#             self.logger.warning(self.status)
#             low_resources = True
#             low_disk = True

#         if not low_resources:
#             self.status = "OK"
#             self.error = None

#         if low_resources:
#             if self.connected:
#                 self.ref_iot_manager.publish_message("alert", self.status)

#         if low_disk:
#             self.clean_up_disk()
#             self.clean_up_database()

#     def valid_internet_connection(self):
#         try:
#             urllib.request.urlopen("http://google.com")
#             return True
#         except:
#             return False

#     def thread_proc(self):
#         disconnected = True
#         while True:
#             if self.stopped():
#                 break

#             if self.valid_internet_connection():
#                 self.connected = True
#                 if disconnected:
#                     self.ref_iot_manager.reset()
#                     disconnected = False
#             else:
#                 self.connected = False
#                 disconnected = True

#             self.update()

#             if self.connected:
#                 time.sleep(300)  # idle for 5 min
#             else:
#                 time.sleep(5)  # fast idle until we get connected
