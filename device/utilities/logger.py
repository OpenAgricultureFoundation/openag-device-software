import logging, sys


class Logger:
	""" Manages logging. Ensures descriptive logs in normal runtime 
		environment and in testing environment. """

	def __init__(self, name, dunder_name):
		""" Initializes logger. """

		# Initialize parameters
		self.name = name

		# Initialize logger
		extra = {'console_name':name, 'file_name': name}
		logger = logging.getLogger(dunder_name)
		self.logger = logging.LoggerAdapter(logger, extra)
		self.debug("Instantiated")


	def debug(self, message):
		""" Reports standard logging debug message if in normal runtime
			environment. If in test environment, prepends message with 
			logger name. """
		if "pytest" in sys.modules:
			self.logger.debug(self.name + ": " + str(message))
		else:
			self.logger.debug(message)


	def info(self, message):
		""" Reports standard info debug message if in normal runtime
			environment. If in test environment, prepends message with 
			logger name. """
		if "pytest" in sys.modules:
			self.logger.info(self.name + ": " + str(message))
		else:
			self.logger.info(message)


	def warning(self, message):
		""" Reports standard logging warning message if in normal runtime
			environment. If in test environment, prepends message with 
			logger name. """
		if "pytest" in sys.modules:
			self.logger.warning(self.name + ": " + str(message))
		else:
			self.logger.warning(message)


	def error(self, message):
		""" Reports standard logging error message if in normal runtime
			environment. If in test environment, prepends message with 
			logger name. """
		if "pytest" in sys.modules:
			self.logger.error(self.name + ": " + str(message))
		else:
			self.logger.error(message)


	def critical(self, message):
		""" Reports standard logging critical message if in normal runtime
			environment. If in test environment, prepends message with 
			logger name. """
		if "pytest" in sys.modules:
			self.logger.critical(self.name + ": " + str(message))
		else:
			self.logger.critical(message)


	def exception(self, message):
		""" Reports standard logging exception message if in normal runtime
			environment. If in test environment, prepends message with 
			logger name. """
		if "pytest" in sys.modules:
			self.logger.exception(self.name + ": " + str(message))
		else:
			self.logger.exception(message)