# Import python modules
import os, sys, glob, logging, subprocess, threading, time, urllib.request

# Import django modules
from django.db import connection  # so we can do raw sql queries

# Import app models
from app.models import EnvironmentModel
from app.models import EventModel

IMAGE_DIR = "data/images/"


class ResourceManager:
    """Manages critical resources: disk space and database capacity."""

    # Initialize logger
    extra = {"console_name": "ResourceManager", "file_name": "resource"}
    logger = logging.getLogger("resource")
    logger = logging.LoggerAdapter(logger, extra)

    # Place holder for thread object.
    thread = None

    def __init__(self, state, ref_device_manager, ref_iot_manager):
        """Initializes manager."""
        self.logger.debug("Initializing manager")

        # Initialize state
        self.state = state
        self.connected = False
        self.error = None
        self.ref_device_manager = ref_device_manager
        self.ref_iot_manager = ref_iot_manager
        self.update()
        self._stop_event = threading.Event()  # so we can stop this thread

    @property
    def error(self):
        """ Gets error value. """
        return self._error

    @error.setter
    def error(self, value):
        """ Safely updates recipe error in shared state. """
        self._error = value
        with threading.Lock():
            self.state.resource["error"] = value

    @property
    def status(self):
        """ Gets status value. """
        return self._status

    @status.setter
    def status(self, value):
        """ Safely updates recipe status in shared state. """
        self._status = value
        with threading.Lock():
            self.state.resource["status"] = value

    @property
    def connected(self):
        return self._connected

    @connected.setter
    def connected(self, value):
        self._connected = value

    def spawn(self):
        self.logger.info("Spawning resource manager thread")
        self.thread = threading.Thread(target=self.thread_proc)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.logger.info("Stopping resource manager thread")
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def get_available_disk_space(self):
        """
        Return the amount of free disk space on Debian and OSX.
        """
        available_disk_space = "Unknown"
        try:
            # command and list of args as list of string
            cmd1 = ["df", "-h", "/"]
            cmd2 = ["awk", "{print $4}"]
            cmd3 = ["tail", "-1"]

            if sys.platform == "darwin":
                cmd1 = ["df", "-hg", "/"]  # for OSX, show in G without chars

            with subprocess.Popen(cmd1, stdout=subprocess.PIPE) as proc1:

                with subprocess.Popen(
                    cmd2, stdin=proc1.stdout, stdout=subprocess.PIPE
                ) as proc2:

                    with subprocess.Popen(
                        cmd3, stdin=proc2.stdout, stdout=subprocess.PIPE
                    ) as proc3:
                        available_disk_space = (
                            proc3.stdout.read().decode("utf-8").rstrip()
                        )

            if sys.platform == "darwin":
                available_disk_space += "G"  # for OSX, add on 'G' like Linux

        except Exception as e:
            available_disk_space = e

        return available_disk_space

    def get_free_memory(self):
        """
        Return a string showing the amount of free RAM in 'M'egabytes on
        Debian/Linux and OSX.
        """
        free_memory = "Unknown"
        try:
            # Linux commands
            cmd1 = ["free", "-ht"]
            cmd2 = ["awk", "{print $4}"]
            cmd3 = ["tail", "-1"]

            if sys.platform == "darwin":
                # OSX commands
                cmd1 = ["top", "-l", "1", "-s", "0"]
                cmd2 = ["grep", "PhysMem"]
                cmd3 = ["awk", "{print $6}"]

            with subprocess.Popen(cmd1, stdout=subprocess.PIPE) as proc1:

                with subprocess.Popen(
                    cmd2, stdin=proc1.stdout, stdout=subprocess.PIPE
                ) as proc2:

                    with subprocess.Popen(
                        cmd3, stdin=proc2.stdout, stdout=subprocess.PIPE
                    ) as proc3:
                        free_memory = proc3.stdout.read().decode("utf-8").rstrip()

        except:
            free_memory = "Unknown"

        return free_memory

    def delete_files(self, path):
        try:
            self.logger.info("Deleting all files in: " + path)
            imageFileList = glob.glob(path)
            for imageFile in imageFileList:
                os.system("rm -f {}".format(imageFile))
        except Exception as e:
            self.logger.error(e)

    def clean_up_disk(self):
        """Delete ALL image files."""
        self.delete_files(IMAGE_DIR + "*.png")
        self.delete_files(IMAGE_DIR + "stored/*.png")

    def clean_up_database(self):
        """Delete all but the most recent 50 events and 
           environments from database."""
        try:
            self.logger.info("Cleaning up database.")
            # clean out the events
            qs = EventModel.objects.all()  # query set of all items
            eventCount = len(qs)
            if 50 < eventCount:
                # delete oldest items ordered by timestamp, leaving at most 50
                deleteUpToIndex = eventCount - 50
                oldest = EventModel.objects.order_by("timestamp")[:deleteUpToIndex]
                for obj in oldest:
                    obj.delete()

            # clean out the environments
            qs = EnvironmentModel.objects.all()  # query set of all items
            eventCount = len(qs)
            if 50 < eventCount:
                # delete oldest items ordered by timestamp, leaving at most 50
                deleteUpToIndex = eventCount - 50
                oldest = EnvironmentModel.objects.order_by("timestamp")[
                    :deleteUpToIndex
                ]
                for obj in oldest:
                    obj.delete()

        except Exception as e:
            self.logger.error(e)

    def get_database_size(self):
        ret = ""
        # must use single quotes within the sql query, not double.
        sql = "select pg_size_pretty( pg_database_size('openag_brain'));"
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                res = cursor.fetchone()
                ret = res[0]
        except Exception as e:
            self.logger.error(e)
            ret = ""
        return ret

    def update(self):
        free_disk = self.get_available_disk_space()
        free_memory = self.get_free_memory()
        database_size = self.get_database_size()

        self.state.resource["available_disk_space"] = free_disk
        self.state.resource["free_memory"] = free_memory
        self.state.resource["database_size"] = database_size
        self.state.resource["internet_connection"] = str(self.connected)

        fd_units = free_disk[-1]  # last char is units: K/M/G
        fm_units = free_memory[-1]  # last char is units: K/M/G

        fd_val = free_disk[0:-1]
        fm_val = free_memory[0:-1]
        self.logger.debug(
            "\n{}, {}, {}, {}".format(
                "free disk={}".format(free_disk),
                "free memory={}".format(free_memory),
                "DB size={}".format(database_size),
                "internet connection={}".format(self.connected),
            )
        )

        # detect low memory and disk space
        low_resources = False
        low_disk = False
        if "K" == fm_units or ("M" == fm_units and 10 <= len(fm_val)):
            # 10M low memory limit
            self.status = "Warning: low memory: {}".format(free_memory)
            self.logger.warning(self.status)
            low_resources = True

        if "K" == fd_units or ("M" == fd_units and 50 <= int(fm_val)):
            # 50M low disk limit
            self.status = "Warning: low disk space: {}".format(free_disk)
            self.logger.warning(self.status)
            low_resources = True
            low_disk = True

        if not low_resources:
            self.status = "OK"
            self.error = None

        if low_resources:
            self.status = "Warning: low resources"
            self.error = "Low resources"
            self.logger.warning(self.error)
            if self.connected:
                self.ref_iot_manager.publishMessage("alert", self.status)

        if low_disk:
            self.clean_up_disk()
            self.clean_up_database()

    def valid_internet_connection(self):
        try:
            urllib.request.urlopen("http://google.com")
            return True
        except:
            return False

    def thread_proc(self):
        disconnected = True
        while True:
            if self.stopped():
                break

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
                time.sleep(300)  # idle for 5 min
            else:
                time.sleep(5)  # fast idle until we get connected
