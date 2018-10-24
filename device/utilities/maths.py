# Import standard python modules
import numpy, math, operator

# Import python types
from typing import List, Union, Dict, Optional


def magnitude(x: float) -> int:
    """Gets magnitude of value."""

    # Check for zero condition
    if x == 0:
        return 0

    # Calculate magnitude and return
    return int(math.floor(math.log10(x)))


def is_sorted_increasing(list_: List[Union[int, float]]) -> bool:
    """Checks if list is sorted in increasing order."""
    return all(list_[i] <= list_[i + 1] for i in range(len(list_) - 1))  # type: ignore


def interpolate(
    x_list: List[Union[int, float]],
    y_list: List[Union[int, float]],
    x: Union[int, float],
) -> Union[int, float]:
    """ Interpolates value for x from x_list and y_list. """

    # Verify x_list and y_list are same length
    if len(x_list) != len(y_list):
        raise ValueError("x_list and y_list must be same length")

    # Verify x_list is sorted
    if not is_sorted_increasing(x_list):

        # Try reversing list and rechecking
        x_list_copy = x_list.copy()
        x_list_copy.reverse()
        if not is_sorted_increasing(x_list_copy):
            raise ValueError("x_list must be sorted")

        # x_list is sorted in decreasing order, need to reverse y_list now
        y_list_copy = y_list.copy()
        y_list_copy.reverse()

    # x_list is sorted in increasing order
    else:
        x_list_copy = x_list.copy()
        y_list_copy = y_list.copy()

    # if x < smallest in list, make that the new x
    if x < x_list_copy[0]:  # type: ignore
        x = x_list_copy[0]

    # if x > largest in list, make that the new x
    if x > x_list_copy[-1]:  # type: ignore
        x = x_list_copy[-1]

    # Check if x matches entry in x_list
    if x in x_list_copy:
        index = x_list_copy.index(x)
        return y_list_copy[index]

    # Get index of smallest element greater than x
    for index in range(len(x_list_copy)):
        if x_list_copy[index] > x:  # type: ignore
            break
    index = index - 1

    # Get values for calculating slope
    x0 = x_list_copy[index]
    x1 = x_list_copy[index + 1]
    y0 = y_list_copy[index]
    y1 = y_list_copy[index + 1]

    # Calculate slope
    m = (y1 - y0) / (x1 - x0)  # type: ignore

    # print("m = {}".format(m))

    # Calculate adjusted position
    delta = x - x0  # type: ignore

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


def bnnls(
    A: numpy.ndarray,
    b: numpy.ndarray,
    bound: float = 1,
    index_map: Optional[Dict] = None,
) -> numpy.ndarray:
    """Solves for bounded non-negative least squares approximation. When solving Ax=b, 
    x is constrained to be within 0-bound."""

    # Solve non-negative least squares approximation
    x = nnls(A, b)
    rows, cols = A.shape

    # Check if x is empty
    if len(x) < 1:
        return x

    # Build initial index map
    if index_map == None:
        index_map = list(range(cols))  # type: ignore

    # Get max column and value
    max_col, max_val = max(enumerate(x.tolist()), key=operator.itemgetter(1))

    # Check for saturated entry in x
    if max_val > bound:

        # Get saturated column
        AT = numpy.transpose(A)
        A_col = AT[max_col]

        # Remove saturated value from b
        new_b = b - A_col * bound

        # Remove saturated column from A
        new_AT = numpy.delete(AT, max_col, 0)
        new_A = numpy.transpose(new_AT)

        # Update index map
        new_index_map = index_map[:]  # type: ignore
        del new_index_map[max_col]

        # Recalculate new x for new A and b
        new_x = bnnls(new_A, new_b, bound=bound, index_map=new_index_map)

        # Build x mapped dictionary
        x_mapped_dict: Dict = {}

        # Add saturated value to x mapped dict
        x_mapped_dict = {index_map[max_col]: bound}  # type: ignore

        # Add remaining values to x mapped dict
        for i, index in enumerate(new_index_map):
            x_mapped_dict[index] = new_x[i]

        # Convert x mapped dict to list
        sorted_keys = sorted(x_mapped_dict)
        x_mapped_list = []
        for key in sorted_keys:
            x_mapped_list.append(x_mapped_dict[key])

        # Return x mapped list
        return x_mapped_list

    else:
        return x


def nnls(A: numpy.ndarray, b: numpy.ndarray, tol: float = 1e-8) -> numpy.ndarray:
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
