class State(object):
	""" Shared memory object used to store and transmit 
		state between threads. """

	device = {}
	environment = {}
	recipe = {}
	peripherals = {}
	controllers = {}