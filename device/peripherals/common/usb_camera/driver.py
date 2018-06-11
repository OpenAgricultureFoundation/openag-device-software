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


    def __init__(self, name, vendor_id, product_id, resolution, directory, simulate=False):
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


    def capture(self) -> Error:
        """ Captures an image. """

        # Check if simulated
        if self.simulate:
            self.logger.info("Simulating capturing image")
            return Error(None)  

        # Capture image
        self.logger.info("Capturing image")   

        # Get camera paths
        cameras = self.list_cameras(self.vendor_id, self.product_id)

        # Check only one active camera
        if len(cameras) < 1:
            return Error("Unable to capture, no active cameras")
        elif len(cameras) > 1:
            return Error("Unable to capture, too many active cameras")

        # Name image according to ISO8601
        timestr = datetime.datetime.utcnow().strftime("%Y-%m-%d-T%H:%M:%SZ")
        filename = timestr  + "_"  + self.name + ".png"

        # Build filepath string
        filepath = self.directory + filename

        # Capture image
        self.logger.info("Capturing image from: {} to: {}".format(cameras[0], filepath))
        try:
            command = 'fswebcam -d {} -r 2592x1944 --background --png 9 --no-banner --save {}'.format(cameras[0], filepath)
            os.system(command)
        except Exception as e:
            return Error("Unable to capture image, unexpected exception: {}".format(e))

        # Successfully captured image
        return Error(None)
