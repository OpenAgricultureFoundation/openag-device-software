import subprocess
from pathlib import Path
import NetworkManager
import RPi.GPIO as GPIO
import device.utilities.led
from typing import Optional, Callable
import time
from device.utilities.network.network_utility_factory import NetworkUtilityFactory

BUTTON_GPIO_LINE = 17  # 0 on our board, I'm using 17 on the Fin


class ButtonHandler:
    button_line: int
    network_reset_time: int
    data_wipe_time: int
    button_pressed: bool
    button_down_time: int
    cancel_time: int
    NET_CONFIGURED: str = "/data/network.configured"

    def __init__(self,
                 button_line: Optional[int] = 0,
                 network_reset_time: Optional[int] = 10,
                 data_wipe_time: Optional[int] = 20,
                 cancel_time: Optional[int] = 30) -> None:
        self.button_line = button_line
        self.network_reset_time = network_reset_time
        self.data_wipe_time = data_wipe_time
        self.cancel_time = cancel_time
        self.setup_gpio()
        self.register_callback()
        self.button_pressed = False
        self.button_down_time = 0

    def is_pressed(self) -> bool:
        return self.button_pressed

    def is_network_reset(self) -> bool:
        now = time.time()
        return self.button_pressed and \
               (now - self.button_down_time >= self.network_reset_time) and \
               (now - self.button_down_time < self.data_wipe_time)

    def is_data_wipe(self) -> bool:
        now = time.time()
        return self.button_pressed and \
               (now - self.button_down_time >= self.data_wipe_time) and \
               (now - self.button_down_time < self.cancel_time)

    def is_canceled(self) -> bool:
        now = time.time()
        return self.button_pressed and (now - self.button_down_time >= self.cancel_time)

    def setup_gpio(self) -> None:
        """
        Initialize the gpio line for a button
        """
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.button_line, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        return

    def reset_network(self):
        Path(self.NET_CONFIGURED).unlink()

        # Get all known connections
        connections = NetworkManager.Settings.ListConnections()

        # Delete the '802-11-wireless' connections
        for connection in connections:
            if connection.GetSettings()["connection"]["type"] == "802-11-wireless":
                #self.logger.debug(
                #    "BalenaNetworkUtility: Deleting connection "
                #    + connection.GetSettings()["connection"]["id"]
                #)
                connection.Delete()

        # Script to call the balena supervisor internal API to reboot the device
        subprocess.call(["scripts/platform/reset_balena_app.sh"])


    def callback_handler(self, channel):
        if not GPIO.input(self.button_line):
            # If it's low, the button was just pressed
            # So set the push time
            self.button_down_time = time.time()
            self.button_pressed = True
        else:
            # Button was just released.
            self.button_pressed = False
            now = time.time()
            if now - self.button_down_time >= self.cancel_time:
                print("Canceling button push")
                return
            elif now - self.button_down_time >= self.data_wipe_time:
                print("WIPING DATA")
                command = ["scripts/platform/reset_balena_app.sh"]

                # Execute command
                try:
                    with subprocess.Popen(
                            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                    ) as process1:
                        output = process1.stdout.read().decode("utf-8")
                        output += process1.stderr.read().decode("utf-8")
                    #self.logger.debug(output)
                except Exception as e:
                    pass
                    #self.logger.exception(
                    #    "Unable to join wifi, unhandled exception: {}".format(type(e))
                    #)
                    #raise
                return
            elif now - self.button_down_time >= self.network_reset_time:
                print("RESETTING NETWORK")
                self.reset_network()
                return


    def register_callback(self):
        GPIO.add_event_detect(self.button_line, GPIO.BOTH, self.callback_handler)


def set_led_color(r: int,g: int,b: int):
    with open("/sys/class/leds/pca963x:red/brightness", 'w') as f:
        f.write(str(r))
    with open("/sys/class/leds/pca963x:green/brightness", 'w') as f:
        f.write(str(g))
    with open("/sys/class/leds/pca963x:blue/brightness", 'w') as f:
        f.write(str(b))


def run():
    """
    Run registers call backs for GPIO line changes, and then starts an infinite loop to stay in the background
    """
    buttonHandler = ButtonHandler(button_line=BUTTON_GPIO_LINE)
    is_reset_lit = False
    is_wipe_lit = False
    was_canceled = False
    while True:
        if buttonHandler.is_pressed():
            if not is_reset_lit and buttonHandler.is_network_reset():
                set_led_color(255,0,255)
                is_reset_lit = True
            elif not is_wipe_lit and buttonHandler.is_data_wipe():
                set_led_color(255,255,255)
                is_wipe_lit = True
            elif not was_canceled and buttonHandler.is_canceled():
                set_led_color(0,0,0)
                was_canceled = True
        elif was_canceled:
            set_led_color(0,25,0)
            was_canceled = False
            is_wipe_lit = False
            is_reset_lit = False


        time.sleep(1)


if __name__ == "__main__":
    run()
