""" Math utility functions. """


def magnitude(x):
    """ Gets magnitude of provided value. """

    # Check for zero condition
    if x == 0:
        return 0

    # Calculate magnitude and return
    return int(math.floor(math.log10(x)))


def interpolate(x_list, y_list, x):
    """ Interpolates value for x from x_list and y_list. """

    # Verify x_list and y_list are same length
    if len(x_list) != len(y_list):
        raise ValueError("x_list and y_list must be same length")

    # Verify x_list is sorted
    if not all(x_list[i] <= x_list[i+1] for i in range(len(x_list)-1)):
        raise ValueError("x_list must be sorted")

    # Verify x in range of x_list
    if x < x_list[0] or x > x_list[-1]:
        raise ValueError("x is not in range of x_list")

    # Check if x matches entry in x_list
    if x in x_list:
        index = x_list.index(x)
        return y_list[index]

    # Get index of smallest element greater than x
    for index in range(len(x_list)):
        if x_list[index] > x:
            break
    index = index - 1

    # Get values for calculating slope
    x0 = x_list[index]
    x1 = x_list[index + 1]
    y0 = y_list[index]
    y1 = y_list[index + 1]

    # Calculate slope
    m = (y1 - y0) / (x1 - x0)

    # Calculate interpolated value and return
    y = m * x
    return y



def discretize(minimum: int, maximum: int, value: float) -> dict:
    """ Discretizes a value across a range. """

    discretized_value = value / (maximum - minimum + 1)
    output = {}
    for counter in range(minimum, maximum + 1):
        output[counter] = discretized_value

    return output