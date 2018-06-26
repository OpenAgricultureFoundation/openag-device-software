# Import standard python libraries
import sys

# Import driver module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.drivers.dac5578 import DAC5578
except:
    # ... if running tests from same dir as dac5578.py
    sys.path.append("../../")
    from device.drivers.dac5578 import DAC5578


def test_init():
    dac5578 = DAC5578("Test", 2, 0x77, simulate=True)


def test_write_output():
    dac5578 = DAC5578("Test", 2, 0x77, simulate=True)

    # Standard reading
    error = dac5578.write_output(0, 50)
    assert error.exists() == False

    # Channel < 0
    try:
        error = dac5578.write_output(-1, 50)
        assert False
    except ValueError:
        assert True

        # Channel > 7
    try:
        error = dac5578.write_output(8, 27.5)
        assert False
    except ValueError:
        assert True

        # Percent < 0
    try:
        error = dac5578.write_output(0, -10.0)
        assert False
    except ValueError:
        assert True

        # Percent > 100
    try:
        error = dac5578.write_output(0, 105.23)
        assert False
    except ValueError:
        assert True


def test_write_outputs():
    dac5578 = DAC5578("Test", 2, 0x77, simulate=True)

    # Empty output dict
    outputs = {}
    error = dac5578.write_outputs(outputs)
    assert error.exists() == False

    # Single output
    outputs = {0: 90.0}
    error = dac5578.write_outputs(outputs)
    assert error.exists() == False

    # Double output
    outputs = {0: 90.0, 1: 100}
    error = dac5578.write_outputs(outputs)
    assert error.exists() == False

    # Full output
    outputs = {0: 90.0, 1: 100, 2: 50, 3: 25, 4: 12.5, 5: 88, 6: 74.4, 7: 77.7}
    error = dac5578.write_outputs(outputs)
    assert error.exists() == False

    # Channel < 0
    outputs = {-1: 90.0}
    try:
        error = dac5578.write_outputs(outputs)
        assert False
    except ValueError:
        assert True

        # Channel > 7
    outputs = {8: 90.0}
    try:
        error = dac5578.write_outputs(outputs)
        assert False
    except ValueError:
        assert True

        # Percent < 0
    outputs = {0: -10.0}
    try:
        error = dac5578.write_outputs(outputs)
        assert False
    except ValueError:
        assert True

        # Percent > 100
    outputs = {0: 105.0}
    try:
        error = dac5578.write_outputs(outputs)
        assert False
    except ValueError:
        assert True

        # Full output
    outputs = {0: 90.0, 1: 100, 2: 50, 3: 25, 4: 12.5, 5: 88, 6: 74.4, 7: 77.7}
    error = dac5578.write_outputs(outputs)
    assert error.exists() == False


def test_read_power_register():
    dac5578 = DAC5578("Test", 2, 0x77, simulate=True)
    powered, error = dac5578.read_power_register()
    print(powered, error)
    assert (
        powered
        == {0: True, 1: True, 2: True, 3: True, 4: True, 5: True, 6: True, 7: True}
    )
    assert error.exists() == False


def test_probe():
    dac5578 = DAC5578("Test", 2, 0x77, simulate=True)
    error = dac5578.probe()
    assert error.exists() == False


def test_turn_on():
    dac5578 = DAC5578("Test", 2, 0x77, simulate=True)
    error = dac5578.turn_on()
    assert error.exists() == False


def test_turn_off():
    dac5578 = DAC5578("Test", 2, 0x77, simulate=True)
    error = dac5578.turn_off()
    assert error.exists() == False
