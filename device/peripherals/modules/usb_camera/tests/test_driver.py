# Import standard python libraries
import sys, os

# Get current working directory
cwd = os.getcwd()
print("Running from: {}".format(cwd))

# Set correct import path
if cwd.endswith("usb_camera"):
    print("Running locally")
    sys.path.append("../../../../")
elif cwd.endswith("openag-device-software"):
    print("Running globally")
else:
    print("Running from invalid location")
    sys.exit(0)

# Import driver
from device.peripherals.modules.usb_camera.driver import USBCameraDriver
   
# Set directory for loading files
if cwd.endswith("usb_camera"):
    os.chdir("../../../../")

# Set directory
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
