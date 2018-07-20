# Import standard python modules
import numpy, math, operator


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
    if not all(x_list[i] <= x_list[i + 1] for i in range(len(x_list) - 1)):
        raise ValueError("x_list must be sorted")

    # if x < smallest in list, make that the new x
    if x < x_list[0]:
        x = x_list[0]

    # if x > largest in list, make that the new x
    if x > x_list[-1]:
        x = x_list[-1]

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

    # Calculate adjusted position
    delta = x - x0

    # Calculate interpolated value and return
    y = y0 + delta * m

    return y


def discretize(minimum: int, maximum: int, value: float) -> dict:
    """ Discretizes a value across a range. """

    discretized_value = value / (maximum - minimum + 1)
    output = {}
    for counter in range(minimum, maximum + 1):
        output[counter] = discretized_value

    return output


def bnnls(A, b, bound):
    """Solves for bounded non-negative least squares approximation. When solving Ax=b, 
    x is constrained to be within 0-bound"""
    x = nnls(A, b)
    mcol, mval = max(enumerate(x.tolist()), key=operator.itemgetter(1))


def nnls(A, b, tol=1e-8):
    """Origninal function by @alexfields

    Solve ``argmin_x || Ax - b ||_2`` for ``x>=0``. This version may be superior to the FORTRAN implementation when ``A`` has more rows than
    columns, and especially when ``A`` is sparse.
    Note that the arguments and return values differ from the FORTRAN implementation; in particular, this implementation does not expect the actual
    design matrix ``A`` nor the RHS vector ``b``, but rather ``A.T.dot(A)`` and ``A.T.dot(b)``. These are smaller than the original ``A`` and ``b``
    iff ``A`` has more rows than columns.
    This function also does not return the residual. The squared residual ``|| Ax-b ||^2`` may be calculated efficiently as:
        ``b.dot(b) + x.dot(A_dot_A.dot(x) - 2*A_dot_b)``
    where ``x`` is the output of this function

    """

    A_dot_A = A.T.dot(A)
    A_dot_b = A.T.dot(b)

    A_dot_A = numpy.asarray_chkfinite(A_dot_A)
    A_dot_b = numpy.asarray_chkfinite(A_dot_b)

    if len(A_dot_A.shape) != 2:
        raise ValueError("expected matrix")
    if len(A_dot_b.shape) != 1:
        raise ValueError("expected vector")

    nvar = A_dot_A.shape[0]
    if nvar != A_dot_A.shape[1]:
        raise ValueError("expected square matrix")

    if nvar != A_dot_b.shape[0]:
        raise ValueError("incompatible dimensions")

    P_bool = numpy.zeros(nvar, numpy.bool)
    x = numpy.zeros(nvar, dtype=A_dot_A.dtype)
    s = numpy.empty_like(x)
    w = A_dot_b
    while not P_bool.all() and w.max() > tol:
        j_idx = w[~P_bool].argmax()
        newly_allowed = numpy.flatnonzero(~P_bool)[j_idx]
        P_bool[newly_allowed] = True
        s[:] = 0
        currPs = numpy.flatnonzero(P_bool)
        if len(currPs) > 1:
            s[currPs] = numpy.linalg.solve(
                A_dot_A[currPs[:, None], currPs[None, :]], A_dot_b[currPs]
            )
        else:
            currP = currPs[0]
            s[currP] = A_dot_b[currP] / A_dot_A[currP, currP]
        s_P_l_0 = s[currPs] < 0
        while s_P_l_0.any():
            currPs_s_P_l_0 = currPs[s_P_l_0]
            alpha = (x[currPs_s_P_l_0] / (x[currPs_s_P_l_0] - s[currPs_s_P_l_0])).min()
            x += alpha * (s - x)
            P_bool[currPs] = x[currPs] > tol
            s[:] = 0
            currPs = numpy.flatnonzero(P_bool)
            if len(currPs) > 1:
                s[currPs] = numpy.linalg.solve(
                    A_dot_A[currPs[:, None], currPs[None, :]], A_dot_b[currPs]
                )
            else:
                currP = currPs[0]
                s[currP] = A_dot_b[currP] / A_dot_A[currP, currP]
            s_P_l_0 = s[currPs] < 0
        x[:] = s[:]
        if x[newly_allowed] == 0:
            break  # avoid infinite loop
        w = A_dot_b - A_dot_A.dot(x)
    return x
