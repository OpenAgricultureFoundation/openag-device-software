# Import standard python libraries
import sys

# Import error module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.utilities.error import Error
except:
    # ... if running tests from same dir as error.py
    sys.path.append("../../")
    from device.utilities.error import Error


def test_init():
    error = Error()
    error = Error(None)
    error = Error("Error 1")


def test_none():
    error = Error()
    assert str(error) == "None"
    assert error.exists() == False
    assert error.latest() == None
    assert error.earliest() == None
    assert error.previous() == None
    assert error.trace == None


def test_single():
    error = Error()
    error.report("Error 1")
    assert str(error) == "Error 1"
    assert error.exists() == True
    assert error.latest() == "Error 1"
    assert error.earliest() == "Error 1"
    assert error.previous() == None
    assert error.trace == "(Error 1)"


def test_clear():
    error = Error()
    error.report("Error 1")
    error.clear()
    assert error.latest() == None


def test_double():
    error = Error()
    error.report("Error 1")
    error.report("Error 2")
    assert error.latest() == "Error 2"
    assert error.earliest() == "Error 1"
    assert error.previous() == "Error 1"
    assert error.trace == "(Error 1) <- (Error 2)"
