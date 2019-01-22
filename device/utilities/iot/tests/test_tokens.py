# Import standard python libraries
import os, sys, pytest, time

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import manager elements
from device.utilities.iot import tokens


def test_init() -> None:
    assert True
