# Import standard python libraries
import os, sys, pytest, threading

# Import python types
from typing import Dict

# Set system path
sys.path.append(str(os.getenv("PROJECT_ROOT", "")))

# Import mux simulator
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

# Import peripheral driver
from device.peripherals.common.adt7470.driver import PCA9633Driver
from device.peripherals.common.adt7470 import exceptions


def test_init() -> None:
    driver = ADT7470Driver(
        "Test",
        i2c_lock=threading.RLock(),
        bus=2,
        address=0x20,
        mux=0x77,
        channel=4,
        simulate=True,
        mux_simulator=MuxSimulator(),
    )
