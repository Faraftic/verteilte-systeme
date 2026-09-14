from time import sleep
import RPi.GPIO as GPIO
import threading


class SoundSensor:

    def update(self):
        while True:
            # Liest den aktuellen Pin-Status (HIGH = Geräusch, LOW = Kein Geräusch)
            state = GPIO.input(self.pin)
            self.result = {"sound_detected": state == GPIO.HIGH}

            if self.result["sound_detected"]:
                print("Sound detected!")
                sleep(0.2)  # Entprellung für Geräusche

            sleep(0.05)

    def __init__(self, pin=18):
        self.pin = pin

        # BOARD-Modus wie in deinem AirSensor-Beispiel
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.result = {"sound_detected": False}

        threading.Thread(target=self.update, daemon=True).start()

    def readSound(self):
        return self.result