class State(object):
	""" A shared memory object used to store and transmit device and thread
	state throughout the system. """

	device = {}
	environment = {}
	recipe = {}
	peripherals = {}
	controllers = {}