# Import standard python libraries
import os, sys, pytest, threading

# Import python types
from typing import Dict

# Set system path
sys.path.append(str(os.getenv("PROJECT_ROOT", "")))

# Import mux simulator
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

# Import peripheral driver
from device.peripherals.common.pca9633.driver import PCA9633Driver
from device.peripherals.common.pca9633 import exceptions


def test_init() -> None:
    driver = PCA9633Driver(
        "Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x20,
        mux=0x77,
        channel=4,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )


# def test_get_port_status_byte() -> None:
#     driver = PCA9633Driver(
#         "Test",
#         i2c_lock=threading.RLock(),
#         bus=2,
#         address=0x20,
#         mux=0x77,
#         channel=4,
#         simulate=True,
#         mux_simulator=MuxSimulator(),
#     )
#     port_status_byte = driver.get_port_status_byte()


# def test_set_low_invalid_port_8() -> None:
#     driver = PCA9633Driver(
#         "Test",
#         i2c_lock=threading.RLock(),
#         bus=2,
#         address=0x20,
#         mux=0x77,
#         channel=4,
#         simulate=True,
#         mux_simulator=MuxSimulator(),
#     )
#     with pytest.raises(exceptions.SetLowError):
#         driver.set_low(8)


# def test_set_low_invalid_port_neg1() -> None:
#     driver = PCA9633Driver(
#         "Test",
#         i2c_lock=threading.RLock(),
#         bus=2,
#         address=0x20,
#         mux=0x77,
#         channel=4,
#         simulate=True,
#         mux_simulator=MuxSimulator(),
#     )
#     with pytest.raises(exceptions.SetLowError):
#         driver.set_low(-1)


# def test_set_low() -> None:
#     driver = PCA9633Driver(
#         "Test",
#         i2c_lock=threading.RLock(),
#         bus=2,
#         address=0x20,
#         mux=0x77,
#         channel=4,
#         simulate=True,
#         mux_simulator=MuxSimulator(),
#     )
#     driver.set_low(2)


# def test_set_high() -> None:
#     driver = PCA9633Driver(
#         "Test",
#         i2c_lock=threading.RLock(),
#         bus=2,
#         address=0x20,
#         mux=0x77,
#         channel=4,
#         simulate=True,
#         mux_simulator=MuxSimulator(),
#     )
#     driver.set_high(2)
