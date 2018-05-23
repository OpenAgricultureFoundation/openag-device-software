# Import standard python libraries
import sys

# Import module...
try:
	# ... if running tests from project root
	sys.path.append(".")
	from device.peripherals.led_dac5578.panel import Panel
except:
	# ... if running tests from same dir as panel.py
	sys.path.append("../../../")
	from device.peripherals.led_dac5578.panel import Panel


def test_init():
	panel = Panel(
		name = "Test",
		bus = 2,
		address = 0x47,
		mux = 0x77,
		channel = 0,
		simulate = True,
	)


def test_initialize():
	panel = Panel("Test", 2, 0x47, mux = 0x77, channel = 0, simulate = True)
	panel.initialize()

