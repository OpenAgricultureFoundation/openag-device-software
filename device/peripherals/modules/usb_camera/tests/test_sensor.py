# Import standard python libraries
import sys, os, json

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

# Import sensor
from device.peripherals.modules.usb_camera.sensor import USBCameraSensor


# Set directory for loading files
if cwd.endswith("usb_camera"):
    os.chdir("../../../../")

# Set directory
directory = "device/peripherals/modules/usb_camera/tests/images/"


def test_init():
    sensor = USBCameraSensor(
        name="Test",
        directory=directory,
        vendor_id=0x05A3,
        product_id=0x9520,
        resolution="640x480",
        simulate=True,
    )


def test_capture():
    sensor = USBCameraSensor(
        "Test", directory, 0x05A3, 0x9520, "640x480", simulate=True
    )
    error = sensor.capture()
    assert error.exists() == False


def test_probe():
    sensor = USBCameraSensor(
        "Test", directory, 0x05A3, 0x9520, "640x480", simulate=True
    )
    error = sensor.probe()
    assert error.exists() == False


def test_reset():
    sensor = USBCameraSensor(
        "Test", directory, 0x05A3, 0x9520, "640x480", simulate=True
    )
    error = sensor.reset()
    assert True
