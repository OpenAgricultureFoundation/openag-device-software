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


def test_bnnls():

    # TODO: Pick better test values for verifying exact math, right now these values are
    # just from the taurus light panel where A is generated from measuring each channel's
    # spectrum and b from measuring spectrum from all channels on...

    A = numpy.array(
        [
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 7.0, 198.0, 40.94, 15.84],
            [0.0, 0.0, 62.3, 2.0, 83.66, 75.24],
            [1.92, 222.46, 0.7, 0.0, 48.06, 97.02],
            [14.08, 4.54, 0.0, 0.0, 5.34, 9.9],
        ]
    )
    b = numpy.array([0.0, 208.0, 176.0, 312.0, 104.0])
    x = bnnls(A, b, bound=1)

    # Round all values to 2 decimals
    for index, value in enumerate(x):
        x[index] = round(value, 2)

    assert x == [1, 0.75, 0.25, 0.75, 1, 1]
