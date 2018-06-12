# Import standard python libraries
import sys, json

# Import sensor module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.modules.elp_usb500w02ml21.camera import ELPUSB500W02ML21Camera
except:
    # ... if running tests from same dir as sensor.py
    sys.path.append("../../../../")
    from device.peripherals.modules.elp_usb500w02ml21.camera import ELPUSB500W02ML21Camera
    

directory = "device/peripherals/modules/elp_usb500w02ml21/tests/images/"


def test_init():
    camera = ELPUSB500W02ML21Camera(
        name = "Camera-1", 
        directory = directory,
        simulate = True,
    )


def test_capture():
    camera = ELPUSB500W02ML21Camera("Camera-1", directory, simulate=True)
    error = camera.capture()
    assert error.exists() == False


def test_probe():
    camera = ELPUSB500W02ML21Camera("Camera-1", directory, simulate=True)
    error = camera.probe()
    assert error.exists() == False


def test_reset():
    camera = ELPUSB500W02ML21Camera("Camera-1", directory, simulate=True)
    error = camera.reset()
    assert True

