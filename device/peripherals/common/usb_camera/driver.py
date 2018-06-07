# Import standard python modules
import time, os, datetime
from typing import Optional, Tuple

# Import pygame
import pygame
import pygame.camera

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

        # Initialize pygame
        pygame.camera.init()


    def get_camera(self) -> Tuple[Optional[pygame.camera.Camera], Error]:
        """ Gets a pygame camera object from stored vendor and product ids. 
            Requires only one active camera at a time. """

        # Check if simulated
        if self.simulate:
            self.logger.info("Simulating getting camera")
            return None, Error(None)

        # Get camera paths that match vendor and product ids
        self.logger.info("Getting camera")
        camera_paths = pygame.camera.list_cameras()
        matched_camera_paths = []
        for camera_path in camera_paths:
            if usb_device_matches(camera_path, self.vendor_id, self.product_id):
                matched_camera_paths.append(camera_path)

        # Check only one active camera
        if len(matched_camera_paths) < 1:
            return None, Error("Unable to get camera, no active cameras")
        elif len(matched_camera_paths) > 1:
            return None, Error("Unable to get camera, too many active cameras")

        # Successfully got camera!
        camera = pygame.camera.Camera(matched_camera_paths[0], self.resolution)
        return camera, Error(None)


    def capture(self) -> Error:
        """ Captures an image. """

        # Check if simulated
        if self.simulate:
            self.logger.info("Simulating capturing image")
            return Error(None)        

        # Get camera
        camera, error = self.get_camera()

        # Check for errors
        if error.exists():
            error.report("Unable to capture image")
            return error

        # Capture image
        self.logger.info("Capturing image")
        camera.start()
        image = camera.get_image()
        camera.stop()

        # Name image according to ISO8601
        timestr = datetime.datetime.utcnow().strftime("%Y-%m-%d-T%H:%M:%SZ")
        filename = timestr  + "_"  + self.name + ".jpg"

        # Save image
        filepath = self.directory + filename
        self.logger.info("Saving image: {}".format(filepath))
        pygame.image.save(image, filepath)

        # Successfully captured image
        return Error(None)
