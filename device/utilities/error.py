# Import standard python modules
from typing import Optional, List, overload


class Error:
	""" Manages errors with trace. """

	def __init__(self, message: Optional[str] = None) -> None:
		""" Initializes error. Can pass in initial error message. """
		if message == None:
			self._trace: List[str] = []
		else:
			self._trace: List[str] = [str(message)]


	def __str__(self) -> str:
		""" Returns latest error. """
		if len(self._trace) > 0:
			return self._trace[-1]
		else:
			return "None"


	def report(self, message: str) -> None:
		""" Reports a new error. """
		self._trace.append(message)


	def clear(self) -> None:
		""" Clears error trace. """
		self._trace = []


	def exists(self) -> bool:
		""" Check if error exists. """
		if len(self._trace) > 0:
			return True
		else:
			return False


	def latest(self) -> Optional[str]:
		""" Returns latest error. """
		if len(self._trace) > 0:
			return self._trace[-1]
		else:
			return None


	def earliest(self) -> Optional[str]:
		""" Return earliest error. """
		if len(self._trace) > 0:
			return self._trace[0]
		else:
			return None


	def previous(self) -> Optional[str]:
		""" Returns previous error. """
		if len(self._trace) > 1:
			return self._trace[-2]
		else:
			return None


	@property
	def trace(self) -> Optional[str]:
		""" Returns error _trace. """

		# Check for empty trace:
		if len(self._trace) < 1:
			return None

		# Build and return response
		response = ""
		for error in self._trace[:-1]:
			response += "({}) -> ".format(error)
		response += "({})".format(self._trace[-1])
		return response
