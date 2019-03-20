# Import standard python modules
import logging, sys, json, os

# Import python types
from typing import Dict, Any

from django.conf import settings


class Logger:
    """Simple logger class. Ensures descriptive logs in run and test environments."""

    def __init__(self, name: str, log: str) -> None:
        """ Initializes logger. """
        self.name = name
        extra = {"console_name": name, "file_name": name}
        logger = logging.getLogger(log)
        self.logger = logging.LoggerAdapter(logger, extra)

    def debug(self, message: str) -> None:
        """ Reports standard logging debug message if in normal runtime
            environment. If in test environment, prepends message with
            logger name. """
        if "pytest" in sys.modules:
            print("DEBUG " + self.name + ": " + str(message))
        else:
            self.logger.debug(message)

    def info(self, message: str) -> None:
        """ Reports standard info debug message if in normal runtime
            environment. If in test environment, prepends message with
            logger name. """
        if "pytest" in sys.modules:
            print("INFO " + self.name + ": " + str(message))
        else:
            self.logger.info(message)

    def warning(self, message: str) -> None:
        """ Reports standard logging warning message if in normal runtime
            environment. If in test environment, prepends message with
            logger name. """
        if "pytest" in sys.modules:
            print("WARNING " + self.name + ": " + str(message))
        else:
            self.logger.warning(message)

    def error(self, message: str) -> None:
        """ Reports standard logging error message if in normal runtime
            environment. If in test environment, prepends message with
            logger name. """
        if "pytest" in sys.modules:
            print("ERROR " + self.name + ": " + str(message))
        else:
            self.logger.error(message)

    def critical(self, message: str) -> None:
        """ Reports standard logging critical message if in normal runtime
            environment. If in test environment, prepends message with
            logger name. """
        if "pytest" in sys.modules:
            print("CRITICAL " + self.name + ": " + str(message))
        else:
            self.logger.critical(message)

    def exception(self, message: str) -> None:
        """ Reports standard logging exception message if in normal runtime
            environment. If in test environment, prepends message with
            logger name. """
        if "pytest" in sys.modules:
            self.logger.exception(self.name + ": " + str(message))
        else:
            self.logger.exception(message)


class PeripheralFileHandler(logging.Handler):
    """Splits each peripheral thread into its own log file."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes peripheral file handler."""

        # Inherit functions from handler
        super().__init__(*args, **kwargs)

        # Get project root dir
        ROOT_DIR = os.environ.get("PROJECT_ROOT")
        if ROOT_DIR != None:
            ROOT_DIR += "/"  # type: ignore
        else:
            ROOT_DIR = ""

        # Load device config
        # DEVICE_CONFIG_PATH = ROOT_DIR + "data/config/device.txt"
        # DATA_PATH = os.getenv("STORAGE_LOCATION", ROOT_DIR + "data")

        DEVICE_CONFIG_PATH = settings.DATA_PATH + "/config/device.txt"

        if os.path.exists(DEVICE_CONFIG_PATH):
            with open(DEVICE_CONFIG_PATH) as f:
                config_name = f.readline().strip()
        else:
            config_name = "unspecified"
        path = ROOT_DIR + "data/devices/{}.json".format(config_name)
        device_config = json.load(open(path))

        # Get peripheral configs
        peripheral_configs = device_config.get("peripherals", {})

        # Ensure peripheral configs are not none
        if peripheral_configs == None:
            peripheral_configs = {}

        # Make sure log directory exists
        # LOG_DIR = ROOT_DIR + "data/logs/peripherals/"
        LOG_DIR = settings.DATA_PATH + "/logs/peripherals/"
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)

        # Clear out old peripheral logs
        for file in os.listdir(LOG_DIR):
            if file.endswith(".log") or file.endswith(".log.1"):
                os.remove(LOG_DIR + file)

        # Initialize peripheral file handlers
        self.file_handlers: Dict = {}
        for peripheral_config in peripheral_configs:
            name = peripheral_config["name"]
            filename = LOG_DIR + name + ".log"
            handlers = logging.handlers  # type: ignore
            self.file_handlers[name] = handlers.RotatingFileHandler(
                filename=filename,
                mode="a",
                maxBytes=200 * 1024,
                backupCount=1,
                encoding=None,
                delay=0,
            )
            self.file_handlers[name].format = self.format

    def emit(self, record: Any) -> None:
        """ Emits a log record. """

        # Format record
        log_entry = self.format(record)

        # Route record to peripheral handler if record contains peripheral name
        for name, handler in self.file_handlers.items():
            if name in log_entry:
                handler.emit(record)
                break


class ControllerFileHandler(logging.Handler):
    """Splits each controller thread into its own log file."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes controller file handler."""

        # Inherit functions from handler
        super().__init__(*args, **kwargs)

        # Get project root dir
        ROOT_DIR = os.environ.get("PROJECT_ROOT")
        if ROOT_DIR != None:
            ROOT_DIR += "/"  # type: ignore
        else:
            ROOT_DIR = ""

        # Load device config
        # DEVICE_CONFIG_PATH = ROOT_DIR + "data/config/device.txt"
        # DATA_PATH = os.getenv("STORAGE_LOCATION", ROOT_DIR + "data")
        DEVICE_CONFIG_PATH = settings.DATA_PATH + "/config/device.txt"

        if os.path.exists(DEVICE_CONFIG_PATH):
            with open(DEVICE_CONFIG_PATH) as f:
                config_name = f.readline().strip()
        else:
            config_name = "unspecified"
        path = ROOT_DIR + "data/devices/{}.json".format(config_name)
        device_config = json.load(open(path))

        # Get controller configs
        controller_configs = device_config.get("controllers", {})

        # Ensure controller configs are not none
        if controller_configs == None:
            controller_configs = {}

        # Make sure log directory exists
        LOG_DIR = settings.DATA_PATH + "/logs/controllers/"
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)

        # Clear out old controller logs
        for file in os.listdir(LOG_DIR):
            if file.endswith(".log") or file.endswith(".log.1"):
                os.remove(LOG_DIR + file)

        # Initialize controller file handlers
        self.file_handlers: Dict = {}
        for controller_config in controller_configs:
            name = controller_config["name"]
            filename = LOG_DIR + name + ".log"
            handlers = logging.handlers  # type: ignore
            self.file_handlers[name] = handlers.RotatingFileHandler(
                filename=filename,
                mode="a",
                maxBytes=200 * 1024,
                backupCount=1,
                encoding=None,
                delay=0,
            )
            self.file_handlers[name].format = self.format

    def emit(self, record: Any) -> None:
        """ Emits a log record. """

        # Format record
        log_entry = self.format(record)

        # Route record to controller handler if record contains controller name
        for name, handler in self.file_handlers.items():
            if name in log_entry:
                handler.emit(record)
                break
