# Import standard python libraries
import sys

# Import error module...
try:
    # ... if running tests from project root
    sys.path.append(".")
except:
    # ... if running tests from same dir as error.py
    sys.path.append("../../")


from device.utilities.maths import *


def test_interpolate():
    x_list = [0, 1, 2, 3, 4]
    y_list = [0, 3, 5, 5, 9]
    x = 3.4
    y = interpolate(x_list, y_list, x)
    assert y == 6.6
