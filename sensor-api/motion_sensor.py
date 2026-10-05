import threading
from time import sleep
import RPi.GPIO as GPIO
class MotionSensor:

    def update(self):
        while True:
            self.result = {
                "motion_detected": GPIO.input(self.motion_pin) == GPIO.HIGH
            }
            sleep(3)

    def __init__(self):
        self.motion_pin = 16
        GPIO.setup(self.motion_pin, GPIO.IN)
        self.result = {"motion_detected": False}

        threading.Thread(target=self.update, daemon=True).start()

    def readMotion(self):
        return self.result