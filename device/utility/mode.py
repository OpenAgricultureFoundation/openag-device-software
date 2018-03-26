class Mode(object):
	""" State machine modes """

	BOOT = "BOOT"
	CONFIG = "CONFIG"
	SETUP = "SETUP"
	INIT = "INIT"
	NOM = "NOM" # Normal operation mode
	ERROR = "ERROR"
	RESET = "RESET"
	WARMING = "WARMING"
	LOAD = "LOAD"
	WAIT = "WAIT"
	PAUSE = "PAUSE"
	RESUME = "RESUME"
	STOP = "STOP"
