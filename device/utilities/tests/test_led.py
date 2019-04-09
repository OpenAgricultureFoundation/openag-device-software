# To run a single test:
# source ~/openag-device-software/venv/bin/activate
# pytest -s -k "test_led" test_led.py
# pytest -s test_led.py

# Import standard python libraries
import sys, os, time

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import sensor
from device.utilities import led


def test_init():
    l = led.LED()

def test_led():
    l = led.LED()
    l.set(0x0F, 0x00, 0x00)
    time.sleep(2)
    l.set(0x00, 0x0F, 0x00)
    time.sleep(2)
    l.set(0x00, 0x00, 0x0F)
    time.sleep(2)
    l.off()

