# Import standard python libraries
import sys, os, json

# Import module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.modules.atlas_ec.manager import AtlasEC
except:
    # ... if running tests from same dir as manger.py
    sys.path.append("../../../../")
    from device.peripherals.modules.atlas_ec.manager import AtlasEC
    
# Import shared memory
from device.state import State

# Change directory for importing files
os.chdir("../../../../")

# Import test config
device_config = json.load(open("device/peripherals/modules/atlas_ec/tests/config.json"))
peripheral_config = device_config["peripherals"][0]

# Set testing variable values
desired_distance_cm = 5
desired_intensity_watts = 100
desired_spectrum_nm_percent = {
    "400-449": 10,
    "449-499": 10,
    "500-549": 30, 
    "550-559": 30,
    "600-649": 10,
    "650-699": 10}

# Initialize state
state = State()

def test_init():
    array = AtlasEC(
        name = "Test",
        state = state,
        config = peripheral_config,
        simulate = True,
    )