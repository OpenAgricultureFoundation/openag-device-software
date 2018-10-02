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
from device.state.main import State

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
            modes.NORMAL: [modes.SHUTDOWN, modes.ERROR], modes.ERROR: [modes.SHUTDOWN]
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
                        free_disk = (process3.stdout.read().decode("utf-8").rstrip())
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
