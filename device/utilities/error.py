# Import standard python modules
from typing import Optional, List


class Error:
	""" Manages errors with trace. """


	def __init__(self) -> None:
		self._trace: List[str] = []


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


	@property
	def latest(self) -> Optional[str]:
		""" Returns latest error. """
		if len(self._trace) > 0:
			return self._trace[-1]
		else:
			return None

	@property
	def earliest(self) -> Optional[str]:
		""" Return earliest error. """
		if len(self._trace) > 0:
			return self._trace[0]
		else:
			return None


	@property
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
			response += "({}) <- ".format(error)
		response += "({})".format(self._trace[-1])
		return response
