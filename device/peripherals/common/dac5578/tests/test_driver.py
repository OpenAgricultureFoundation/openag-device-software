# Import standard python libraries
import os, sys, pytest, threading

# Import python types
from typing import Dict

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import mux simulator
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

# Import peripheral driver
from device.peripherals.common.dac5578.driver import DAC5578Driver
from device.peripherals.common.dac5578.exceptions import (
    WriteOutputError,
    WriteOutputsError,
)


def test_init() -> None:
    driver = DAC5578Driver(
        "Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x4C,
        mux=0x77,
        channel=4,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )


def test_write_output_standard() -> None:
    driver = DAC5578Driver(
        "Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x4C,
        mux=0x77,
        channel=4,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    driver.write_output(0, 0)


def test_write_output_channel_lt() -> None:
    driver = DAC5578Driver(
        "Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x4C,
        mux=0x77,
        channel=4,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    with pytest.raises(WriteOutputError):
        driver.write_output(-1, 0)


def test_write_output_channel_gt() -> None:
    driver = DAC5578Driver(
        "Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x4C,
        mux=0x77,
        channel=4,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    with pytest.raises(WriteOutputError):
        driver.write_output(8, 0)


def test_write_output_percent_lt() -> None:
    driver = DAC5578Driver(
        "Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x4C,
        mux=0x77,
        channel=4,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    with pytest.raises(WriteOutputError):
        driver.write_output(0, -1)


def test_write_output_percent_gt() -> None:
    driver = DAC5578Driver(
        "Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x4C,
        mux=0x77,
        channel=4,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    with pytest.raises(WriteOutputError):
        driver.write_output(0, 101)


def test_write_outputs_standard() -> None:
    driver = DAC5578Driver(
        "Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x4C,
        mux=0x77,
        channel=4,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    outputs = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
    driver.write_outputs(outputs)


def test_write_outputs_dict_lt() -> None:
    driver = DAC5578Driver(
        "Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x4C,
        mux=0x77,
        channel=4,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    with pytest.raises(WriteOutputsError):
        outputs: Dict = {}
        driver.write_outputs(outputs)


def test_write_outputs_dict_gt() -> None:
    driver = DAC5578Driver(
        "Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x4C,
        mux=0x77,
        channel=4,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    with pytest.raises(WriteOutputsError):
        outputs = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0}
        driver.write_outputs(outputs)


def test_read_power_register() -> None:
    driver = DAC5578Driver(
        "Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x4C,
        mux=0x77,
        channel=4,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    powered_channels = driver.read_power_register()
    assert powered_channels == {
        0: True,
        1: True,
        2: True,
        3: True,
        4: True,
        5: True,
        6: True,
        7: True,
    }


def test_set_low() -> None:
    driver = DAC5578Driver(
        "Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x4C,
        mux=0x77,
        channel=4,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    driver.set_low()


def test_set_high() -> None:
    driver = DAC5578Driver(
        "Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x4C,
        mux=0x77,
        channel=4,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
    driver.set_high()
