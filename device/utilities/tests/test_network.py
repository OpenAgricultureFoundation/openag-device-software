# Import standard python libraries
import sys, os

# Set system path
ROOT_PATH = os.environ["OPENAG_BRAIN_ROOT"]
sys.path.append(ROOT_PATH)
os.chdir(ROOT_PATH)

# Import connect utility
from device.utilities import network


def test_get_wifi_access_points() -> None:
    wifi_access_points = network.get_wifi_access_points()
    assert wifi_access_points != []
