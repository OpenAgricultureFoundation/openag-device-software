# Import standard python libraries
import sys

# Import health module...
try:
	# ... if running tests from project root
	sys.path.append(".")
	from device.utilities.health import Health
except:
	# ... if running tests from same dir as health.py
	sys.path.append("../../")
	from device.utilities.health import Health


def test_update():
	health = Health(updates=4, minimum=51)

	# One good
	health.update(1)
	assert health.percent == 100
	assert health.healthy == True

	# One good, one bad
	health.update(0)
	assert health.percent == 50
	assert health.healthy == False

	# Len(queue) == updates
	health.update(1)
	health.update(1)
	assert health.percent == 75

	# Len(queue) > updates
	health.update(0)
	assert health.percent == 50
