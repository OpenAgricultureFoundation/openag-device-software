# Import standard python libraries
import os, sys, pytest, numpy

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import device utilities
from device.utilities import accessors


def test_listify_dict() -> None:
    dict_ = {"a": 1, "b": 2}
    expected = [1, 2]
    list_ = accessors.listify_dict(dict_)
    assert list_ == expected


def test_vectorize_dict() -> None:
    dict_ = {"a": 1, "b": 2}
    expected = numpy.array([1, 2])
    vector = accessors.vectorize_dict(dict_)
    assert vector.tolist() == expected.tolist()


def test_matrixify_nested_dict() -> None:
    ndict = {"a": {"b": 1, "c": 2}, "d": {"e": 3, "f": 4}}
    expected = numpy.array([[1, 3], [2, 4]])
    matrix = accessors.matrixify_nested_dict(ndict)
    assert matrix.tolist() == expected.tolist()
