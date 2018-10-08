# Import standard python libraries
import os, sys, pytest, glob, threading

# Import python types
from typing import List

# Set system path and directory
root_dir = os.environ["OPENAG_BRAIN_ROOT"]
sys.path.append(root_dir)
os.chdir(root_dir)

# Import mux simulator
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

# Import peripheral driver
from device.peripherals.modules.usb_camera.driver import USBCameraDriver

# Set test image directory
IMAGE_DIR = "device/peripherals/modules/usb_camera/tests/images/"


def delete_test_images() -> None:
    filelist = glob.glob(os.path.join(IMAGE_DIR, "*.png"))
    for f in filelist:
        os.remove(f)


def list_test_images() -> List[str]:
    return glob.glob(os.path.join(IMAGE_DIR, "*.png"))


def test_init() -> None:
    driver = USBCameraDriver(
        name="Test",
        resolution="640x480",
        vendor_id=0x05A3,
        product_id=0x9520,
        simulate=True,
        mux_simulator=MuxSimulator(),
        i2c_lock=threading.RLock(),
    )


def test_capture() -> None:
    delete_test_images()
    driver = USBCameraDriver(
        name="Test",
        resolution="640x480",
        vendor_id=0x05A3,
        product_id=0x9520,
        simulate=True,
        mux_simulator=MuxSimulator(),
        i2c_lock=threading.RLock(),
    )
    driver.capture()
    images = list_test_images()
    assert len(images) == 1
