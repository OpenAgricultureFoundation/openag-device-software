# Import standard python libraries
import sys

# Import module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.led_dac5578.array import Array
except:
    # ... if running tests from same dir as panel.py
    sys.path.append("../../../")
    from device.peripherals.led_dac5578.array import Array


panels = [
    {
        "name": "Test-1",
        "bus": 2,
        "address": 0x47,
        "mux": 0x77,
        "channel": 0,
    },
    {
        "name": "Test-2",
        "bus": 2,
        "address": 0x47,
        "mux": 0x77,
        "channel": 1,
    }
]

def test_init():
    array = Array("Test", panels, simulate=True)
    assert False
