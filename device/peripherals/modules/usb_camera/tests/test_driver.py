# Import standard python libraries
import sys, os

# Import driver module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.modules.usb_camera.driver import USBCameraDriver
except:
    # ... if running tests from same dir as driver.py
    sys.path.append("../../../../")
    from device.peripherals.modules.usb_camera.driver import USBCameraDriver
   

os.chdir("../../../../")
directory = "device/peripherals/modules/usb_camera/tests/images/" 

def test_init():
    driver = USBCameraDriver(
        name = "Test",
        resolution = (2592, 1944),
        vendor_id = 0x05A3,
        product_id = 0x9520,
        directory = directory,
        simulate = True,
    )

def test_capture():
    driver = USBCameraDriver("Test", (2592, 1944), 0x05A3, 0x9520, directory, simulate=True)
    error = driver.capture()
    assert error.exists() == False
    assert False