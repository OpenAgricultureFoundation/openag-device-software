# Import standard python libraries
import sys, os

# Set system path
ROOT_DIR = os.environ["OPENAG_BRAIN_ROOT"]
sys.path.append(ROOT_DIR)
os.chdir(ROOT_DIR)

# Import connect utility
from device.utilities import system


def test_is_wifi_bbb() -> None:
    wifi_access_points = network.is_wifi_bbb()
    assert wifi_access_points != []
