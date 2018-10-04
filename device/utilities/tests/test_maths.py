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


# def test_interpolate():
#     x_list = [0, 1, 2, 3, 4]
#     y_list = [0, 3, 5, 5, 9]
#     x = 3.4
#     y = interpolate(x_list, y_list, x)
#     assert y == 6.6


def test_interpolate2():
    x_list = [
        0.0,
        5.0,
        10.0,
        15.0,
        20.0,
        25.0,
        30.0,
        35.0,
        40.0,
        45.0,
        50.0,
        55.0,
        60.0,
        65.0,
        70.0,
        75.0,
        80.0,
        85.0,
        90.0,
        95.0,
        100.0,
    ]
    y_list = [
        100.0,
        100.0,
        94.4,
        88.2,
        82.0,
        76.2,
        69.7,
        63.0,
        56.1,
        49.7,
        42.5,
        35.3,
        28.0,
        21.0,
        13.2,
        5.3,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    ]
    x = 22.5
    y = interpolate(x_list, y_list, x)
    assert y == 79.1


def test_interpolate2_reverse():
    x_list = [
        0.0,
        5.0,
        10.0,
        15.0,
        20.0,
        25.0,
        30.0,
        35.0,
        40.0,
        45.0,
        50.0,
        55.0,
        60.0,
        65.0,
        70.0,
        75.0,
        80.0,
        85.0,
        90.0,
        95.0,
        100.0,
    ]
    y_list = [
        100.0,
        100.0,
        94.4,
        88.2,
        82.0,
        76.2,
        69.7,
        63.0,
        56.1,
        49.7,
        42.5,
        35.3,
        28.0,
        21.0,
        13.2,
        5.3,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    ]
    y = 79.1
    x = interpolate(y_list, x_list, y)
    assert round(x, 1) == 22.5


# def test_bnnls():

#     # TODO: Pick better test values for verifying exact math, right now these values are
#     # just from the taurus light panel where A is generated from measuring each channel's
#     # spectrum and b from measuring spectrum from all channels on...

#     A = numpy.array(
#         [
#             [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#             [0.0, 0.0, 7.0, 198.0, 40.94, 15.84],
#             [0.0, 0.0, 62.3, 2.0, 83.66, 75.24],
#             [1.92, 222.46, 0.7, 0.0, 48.06, 97.02],
#             [14.08, 4.54, 0.0, 0.0, 5.34, 9.9],
#         ]
#     )
#     b = numpy.array([0.0, 208.0, 176.0, 312.0, 104.0])
#     x = bnnls(A, b, bound=1)

#     # Round all values to 2 decimals
#     for index, value in enumerate(x):
#         x[index] = round(value, 2)

#     assert x == [1, 0.75, 0.25, 0.75, 1, 1]
