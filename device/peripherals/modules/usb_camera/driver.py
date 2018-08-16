# Import standard python modules
import time, os, datetime, glob, threading
from typing import Optional, Tuple

# Import device comms
from device.comms.i2c import I2C

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error
from device.utilities.accessors import usb_device_matches

# Import peripheral modules
from device.peripherals.common.dac5578.driver import DAC5578


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
        if usb_mux_comms == None or usb_mux_channel == None:
            self.dac5578 = None
            return

        # Using usb mux, initialize driver
        self.dac5578 = DAC5578(
            name=name,
            bus=usb_mux_comms.get("bus", None),
            address=int(usb_mux_comms.get("address", None), 16),
            mux=int(usb_mux_comms.get("mux", None), 16),
            channel=usb_mux_comms.get("channel", None),
            simulate=simulate,
        )
        self.usb_mux_channel = usb_mux_channel

    def probe(self):
        """Probe camera."""

        # Do we want this?
        ...

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
        """Gets camera path."""

        # Get camera paths that match vendor and product ID
        cameras = self.list_cameras(self.vendor_id, self.product_id)

        # Check only one active camera
        if len(cameras) < 1:
            return None, Error("Driver unable to get camera, no active cameras")
        elif len(cameras) > 1:
            return None, Error("Driver unable to get camera, too many active cameras")

        # Successfuly got camera!
        return cameras[0], Error(None)

    def enable_camera(self) -> Error:
        """Enables camera by setting dac output high."""
        self.logger.debug("Enabling camera")

        # Turn on usb mux channel
        error = self.dac5578.set_high(channel=self.usb_mux_channel)

        # Check for error
        if error.exists():
            return error

        # Wait for camera to initialize
        time.sleep(5)

        # Successfully enabled camera
        return Error(None)

    def disable_camera(self) -> Error:
        """Disables camera by setting dac output low."""
        self.logger.debug("Disabling camera")

        # Turn off usb mux channel
        error = self.dac5578.set_low(channel=self.usb_mux_channel)

        # Check for error
        if error.exists():
            return error

        # Wait for camera to power down
        start_time = time.time()
        while True:  # 5 second timeout

            # Look for camera
            try:
                camera, error = self.get_camera()

                # Check if camera powered down
                if camera == None:
                    self.logger.debug("Camera powered down")
                    return Error(None)

            # TODO: Handle specific exceptions
            except:
                self.logger.debug("Camera powered down")
                return Error(None)

            # Check for timeout
            if time.time() - start_time > 5:  # 5 second timeout
                return Error("Unable to disable camera, timed out")

            # Update every 100ms
            time.sleep(0.1)

        # Successfully disabled camera
        return Error(None)

    def capture(self) -> Error:
        """Manages usb mux and captures an image."""

        # Check for usb mux
        if self.dac5578 == None:
            return self.capture_image()

        # Using usb mux
        # Keep thread locked while capturing image / managing usb mux
        # TODO: Is there a better way to do this?
        with threading.Lock():
            try:
                # Enable camera
                error = self.enable_camera()

                # Check for error
                if error.exists():
                    return error

                # Take image
                error = self.capture_image()

                # Check for error
                if error.exists():
                    return error
            except:
                ...
            finally:

                # Disable camera
                self.disable_camera()

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

            command = "fswebcam -d {} -r {} --png 9 --no-banner --save {}".format(
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
