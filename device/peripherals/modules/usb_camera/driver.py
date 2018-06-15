# Import standard python modules
import time, os, datetime, glob
from typing import Optional, Tuple

# Import device comms
from device.comms.i2c import I2C

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error
from device.utilities.accessors import usb_device_matches


class USBCameraDriver:
    """ Driver for a usb camera. """


    def __init__(self, name: str, vendor_id: int, product_id: int, resolution: str, directory: str, simulate=False):
        """ Initializes USB camera camera. """

        # Initialize parametersrecent
        self.name = name
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.resolution = resolution
        self.directory = directory
        self.simulate = simulate

        # Initialize logger
        self.logger = Logger(
            name = "Driver({})".format(name),
            dunder_name = __name__,
        )

        # Check directory exists else create it
        if not os.path.exists(directory):
            os.makedirs(directory)


    def list_cameras(self, vendor_id: int = None, product_id: int = None):
        """ Returns list of cameras that match the provided vendor id and 
            product id. """

        # List all cameras
        cameras = glob.glob("/dev/video*")

        # Check if filtering by product and vendor id
        if vendor_id == None and product_id == None:
            return cameras

        # Check for product and vendor id matches
        matches = []
        for camera in cameras:
            if usb_device_matches(camera, vendor_id, product_id):
                matches.append(camera)
        return matches


    def get_camera(self) -> Tuple[Optional[str], Error]:
        """ Gets camera paths. """

        # Get camera paths that match vendor and product ID
        cameras = self.list_cameras(self.vendor_id, self.product_id)

        # Check only one active camera
        if len(cameras) < 1:
            return None, Error("Driver unable to get camera, no active cameras")
        elif len(cameras) > 1:
            return None, Error("Driver unable to get camera, too many active cameras")

        # Successfuly got camera!
        return cameras[0], Error(None)


    def capture(self) -> Error:
        """ Captures an image. """
        self.logger.info("Capturing image")

        # Name image according to ISO8601
        timestr = datetime.datetime.utcnow().strftime("%Y-%m-%d-T%H:%M:%SZ")
        filename = timestr  + "_"  + self.name + ".png"

        # Build filepath string
        filepath = self.directory + filename

        # Check if simulated
        if self.simulate:
            self.logger.info("Simulating saving image to: {}".format(filepath))
            command = "cp device/peripherals/modules/usb_camera/simulation_image.png {}".format(filepath)
            os.system(command)
            return Error(None)  

        # Camera not simulated!
        camera, error = self.get_camera()

        # Check for errors
        if error.exists():
            error.report("Driver unable to capture image")
            self.logger.error(error.summary())
            return error

        # Capture image
        self.logger.info("Capturing image from: {} to: {}".format(camera, filepath))
        try:

            # TODO: Can we increase resolution? Spec says 2592x1944 but fswebcam returns garbled image...
           
            command = 'fswebcam -d {} -r {} --background --png 9 --no-banner --save {}'.format(camera, self.resolution, filepath)
            os.system(command)
        except Exception as e:
            return Error("Driver unable to capture image, unexpected exception: {}".format(e))

        # TODO: Wait for file in destination and do some prelim checks:
        #  - filesize not too small?
        #  - all black? all white?

        # Successfully captured image
        return Error(None)
