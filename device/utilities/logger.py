import logging, sys, json, os


class Logger:
    """ Manages logging. Ensures descriptive logs in normal runtime 
        environment and in testing environment. """

    def __init__(self, name: str, dunder_name: str) -> None:
        """ Initializes logger. """
        self.name = name
        extra = {"console_name": name, "file_name": name}
        logger = logging.getLogger(dunder_name)
        self.logger = logging.LoggerAdapter(logger, extra)

    def debug(self, message: str) -> None:
        """ Reports standard logging debug message if in normal runtime
            environment. If in test environment, prepends message with 
            logger name. """
        if "pytest" in sys.modules:
            self.logger.debug(self.name + ": " + str(message))
        else:
            self.logger.debug(message)

    def info(self, message: str) -> None:
        """ Reports standard info debug message if in normal runtime
            environment. If in test environment, prepends message with 
            logger name. """
        if "pytest" in sys.modules:
            self.logger.info(self.name + ": " + str(message))
        else:
            self.logger.info(message)

    def warning(self, message: str) -> None:
        """ Reports standard logging warning message if in normal runtime
            environment. If in test environment, prepends message with 
            logger name. """
        if "pytest" in sys.modules:
            self.logger.warning(self.name + ": " + str(message))
        else:
            self.logger.warning(message)

    def error(self, message: str) -> None:
        """ Reports standard logging error message if in normal runtime
            environment. If in test environment, prepends message with 
            logger name. """
        if "pytest" in sys.modules:
            self.logger.error(self.name + ": " + str(message))
        else:
            self.logger.error(message)

    def critical(self, message: str) -> None:
        """ Reports standard logging critical message if in normal runtime
            environment. If in test environment, prepends message with 
            logger name. """
        if "pytest" in sys.modules:
            self.logger.critical(self.name + ": " + str(message))
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
    """ Splits each peripheral thread into its own log file. """

    def __init__(self, *args, **kwargs):
        """ Initializes peripheral file handler. """

        # Inherit functions from handler
        super().__init__(*args, **kwargs)

        # Load about file
        about = json.load(open("about.json"))

        # Load device config file
        config_name = about["device_config"]
        device_config = json.load(open("data/devices/{}.json".format(config_name)))

        # Get peripheral configs
        peripheral_configs = device_config["peripherals"]

        # Clear out old peripheral logs
        for file in os.listdir("logs/peripherals/"):
            if file.endswith(".log") or file.endswith(".log.1"):
                os.remove("logs/peripherals/" + file)

        # Initialize peripheral file handlers
        self.file_handlers = {}
        for peripheral_config in peripheral_configs:
            name = peripheral_config["name"]
            filename = "logs/peripherals/" + name + ".log"
            self.file_handlers[name] = logging.handlers.RotatingFileHandler(
                filename=filename,
                mode="a",
                maxBytes=5 * 1024 * 1024,
                backupCount=1,
                encoding=None,
                delay=0,
            )
            self.file_handlers[name].format = self.format

    def emit(self, record):
        """ Emits a log record. """

        # Format record
        log_entry = self.format(record)

        # Route record to peripheral handler if record contains peripheral name
        for name, handler in self.file_handlers.items():
            if name in log_entry:
                handler.emit(record)
                break
