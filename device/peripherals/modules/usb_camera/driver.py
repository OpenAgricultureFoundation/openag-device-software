# Import standard python modules
import time, os, datetime, glob, threading
from typing import Optional, Tuple

# Import device comms
from device.comms.i2c import I2C

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error
from device.utilities.accessors import usb_device_matches


class USBCameraDriver:
    """Driver for a usb camera."""

    def __init__(
        self,
        name: str,
        vendor_id: int,
        product_id: int,
        resolution: str,
        directory: str,
        simulate=False,
        usb_mux_comms=None,
        usb_mux_channel=None,
    ):
        """Initializes USB camera camera."""

        # Initialize parameters
        self.name = name
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.resolution = resolution
        self.directory = directory
        self.simulate = simulate

        # Initialize logger
        self.logger = Logger(name="Driver({})".format(name), dunder_name=__name__)

        # Check directory exists else create it
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Check is using usb mux
        if usb_mux_comms != None and usb_mux_channel != None:
            self.usb_mux = DAC5578(
                name=name,
                bus=usb_mux_comms.get("bus", None),
                address=usb_mux_comms.get("address", None),
                mux=usb_mux_comms.get("mux", None),
                channel=usb_mux_comms.get("channel", None),
                simulate=simulate,
            )
            self.usb_mux_channel = usb_mux_channel
        else:
            self.usb_mux = None

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
        """Gets camera paths."""
        self.logger.debug("Getting camera")

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
        """Manages usb mux and captures an image."""

        # Keep thread locked while capturing image / managing usb mux
        # TODO: Is there a better way to do this?
        with threading.Lock():

            # Turn on usb mux channel if enable
            if self.usb_mux != None:
                error = self.usb_mux.write_output(self.usb_mux_channel, 100)

                # Check for error
                if error.exists():
                    return error

            # Capture image
            error = self.capture_image()

            # Check for error
            if error.exists():
                return error

            # Turn off usb mux channel
            if self.usb_mux != None:
                error = self.usb_mux.write_output(self.usb_mux_channel, 0)

                # Check for error
                if error.exists():
                    return error

        # Successfully captured image
        return Error(None)

    def capture_image(self) -> Error:
        """Captures an image."""

        # Name image according to ISO8601
        timestr = datetime.datetime.utcnow().strftime("%Y-%m-%d-T%H:%M:%SZ")
        filename = timestr + "_" + self.name + ".png"

        # Build filepath string
        filepath = self.directory + filename

        # Check if simulated
        if self.simulate:
            self.logger.info("Simulating saving image to: {}".format(filepath))
            command = "cp device/peripherals/modules/usb_camera/simulation_image.png {}".format(
                filepath
            )
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

            command = "fswebcam -d {} -r {} --background --png 9 --no-banner --save {}".format(
                camera, self.resolution, filepath
            )
            self.logger.debug("command = {}".format(command))
            os.system(command)

        except Exception as e:
            return Error(
                "Driver unable to capture image, unexpected exception: {}".format(e)
            )

        # TODO: Wait for file in destination and do some prelim checks:
        #  - filesize not too small?
        #  - all black? all white?

        # Successfully captured image
        return Error(None)
