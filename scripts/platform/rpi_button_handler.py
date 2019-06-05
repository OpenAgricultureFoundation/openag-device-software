import RPi.GPIO as GPIO
import device.utilities.led
from typing import Optional, Callable
import time

BUTTON_GPIO_LINE = 17  # 0 on our board, I'm using 17 on the Fin


class ButtonHandler:
    button_line: int
    network_reset_time: int
    data_wipe_time: int
    button_pressed: bool
    button_down_time: int

    def __init__(self,
                 button_line: Optional[int] = 0,
                 network_reset_time: Optional[int] = 30,
                 data_wipe_time: Optional[int] = 120) -> None:
        self.button_line = button_line
        self.network_reset_time = network_reset_time
        self.data_wipe_time = data_wipe_time
        self.setup_gpio()
        self.register_callback()
        self.button_pressed = False
        self.button_down_time = 0

    def setup_gpio(self) -> None:
        """
        Initialize the gpio line for a button
        """
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.button_line, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        return

    def callback_handler(self):
        if not GPIO.input(self.button_line):
            # If it's low, the button was just pressed
            # So set the push time
            self.button_down_time = time.time()
            self.button_pressed = True
        else:
            # Button was just released.
            self.button_pressed = False
            now = time.time()
            if now - self.button_down_time > self.data_wipe_time:
                print("WIPING DATA?")
                # Wipe the data
                pass
            elif now - self.button_down_time > self.network_reset_time:
                print("RESETTING NETWORK")
                # Reset the networking
                pass

    def register_callback(self):
        GPIO.add_event_detect(self.button_line, GPIO.BOTH, self.callback_handler)


def run():
    """
    Run registers call backs for GPIO line changes, and then starts an infinite loop to stay in the background
    """
    buttonHandler = ButtonHandler(button_line=BUTTON_GPIO_LINE)
    while True:
        time.sleep(1)


if __name__ == "__main__":
    run()
