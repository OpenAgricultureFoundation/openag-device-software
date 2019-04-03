import threading
import os
import datetime
import time

from typing import Optional, Dict, Any

from picamera import PiCamera

from device.peripherals.modules.camera.drivers.base_driver import CameraDriver
from device.utilities.communication.i2c.mux_simulator import MuxSimulator

PLATFORM = os.getenv("PLATFORM")


class PiCameraDriver(CameraDriver):
    def __init__(
            self,
            name: str,
            vendor_id: int,
            product_id: int,
            resolution: str,
            num_cameras: int = 1,
            simulate: bool = False,
            usb_mux_comms: Optional[Dict[str, Any]] = None,
            usb_mux_channel: Optional[int] = None,
            i2c_lock: Optional[threading.RLock] = None,
            mux_simulator: Optional[MuxSimulator] = None
    ) -> None:

        # pi camera is only for Raspberry Pi.
        if PLATFORM is not None and PLATFORM == "raspberry-pi":
            self.camera = PiCamera()
            picam_loaded = True
            self.simulate = simulate
        else:
            self.simulate = True
            picam_loaded = False

        super().__init__(name=name,
                         vendor_id=vendor_id,
                         product_id=product_id,
                         resolution=resolution,
                         num_cameras=num_cameras,
                         simulate=self.simulate,
                         usb_mux_comms=usb_mux_comms,
                         usb_mux_channel=usb_mux_channel,
                         i2c_lock=i2c_lock,
                         mux_simulator=mux_simulator)

        if not picam_loaded:
            self.logger.info(
                "pi_camera module: Not running on raspberry-pi OS. Turning on simulation mode."
            )

    def capture(self, retry: bool = True) -> None:
        """Captures an image from a camera or set of non-unique cameras."""
        super().capture(retry=retry)

        timestring = datetime.datetime.utcnow().strftime("%Y-%m-%d_T%H-%M-%SZ")
        filename = self.directory + "{}_{}.png".format(timestring, self.name)

        # Check if simulated
        # if self.simulate:
        #    message = "Simulating capture, saving image to: {}".format(filename)
        #    self.logger.info(message)
        #    command = "cp {} {}".format(self.SIMULATION_IMAGE_PATH, filename)
        #    os.system(command)
        #    return

        # Capture image
        if not self._simulate_capture(filename):
            resolution_array = self.resolution.split("x")
            self.camera.resolution = (int(resolution_array[0]), int(resolution_array[1]))
            self.camera.start_preview()
            # Camera warm-up time
            time.sleep(2)
            # Get timestring in ISO8601 format

            self.camera.capture(filename)
            self.camera.stop_preview()

        return
