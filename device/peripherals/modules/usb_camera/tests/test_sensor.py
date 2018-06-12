# Import standard python libraries
import sys, json

# Import sensor module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.modules.usb_camera.sensor import USBCameraSensor
except:
    # ... if running tests from same dir as sensor.py
    sys.path.append("../../../../")
    from device.peripherals.modules.usb_camera.sensor import USBCameraSensor
    

directory = "device/peripherals/modules/usb_camera/tests/images/"


def test_init():
    sensor = USBCameraSensor(
        name = "Camera-1", 
        directory = directory,
        vendor_id = 0x05A3,
        product_id = 0x9520,
        resolution = "640x480",
        simulate = True,
    )


def test_capture():
    sensor = USBCameraSensor("Camera-1", directory, 0x05A3, 0x9520, "640x480", simulate=True)
    error = sensor.capture()
    assert error.exists() == False


def test_probe():
    sensor = USBCameraSensor("Camera-1", directory, 0x05A3, 0x9520, "640x480", simulate=True)
    error = sensor.probe()
    assert error.exists() == False


def test_reset():
    sensor = USBCameraSensor("Camera-1", directory, 0x05A3,0x9520, "640x480", simulate=True)
    error = sensor.reset()
    assert True

