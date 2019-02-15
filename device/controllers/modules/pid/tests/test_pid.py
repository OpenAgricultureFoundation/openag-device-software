# Import standard python libraries
import os, sys, json, pytest, time

# Set system path and directory
ROOT_DIR = str(os.getenv("PROJECT_ROOT", "."))
sys.path.append(ROOT_DIR)
os.chdir(ROOT_DIR)

# Import PID class
from device.controllers.modules.pid.pid import PID

# Run this test individually:
#   source ~/openag-device-software/venv/bin/activate
#   cd ~/openag-device-software/device/controllers/modules/pid/tests/
#   python -m pytest -s test_pid.py

# ------------------------------------------------------------------------------
def test_init() -> None:
    P: float = 0.2
    I: float = 0.0
    D: float = 0.0
    L: int = 100
    pid: PID = PID(P, I, D)


# ------------------------------------------------------------------------------
def test_PID() -> None:
    P: float = 1.2
    I: float = 1.0
    D: float = 0.001
    L: int = 100

    pid: PID = PID(P, I, D)
    pid.setSetPoint(-30.0)
    pid.setSampleTime(0.01)

    feedback: float = 0

    i: int = 0
    for i in range(1, L):
        pid.update(feedback)
        if pid.getSetPoint() > 0:
            feedback += pid.getOutput() - (1 / i)
        time.sleep(0.02)

    assert pid.getOutput() == -56.0
    assert pid.getSetPoint() == -30.0
