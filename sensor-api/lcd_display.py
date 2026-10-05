import time
import json
import os
import board
import busio
import adafruit_character_lcd.character_lcd_i2c as character_lcd
import paho.mqtt.client as mqtt

LCD_COLUMNS = 16
LCD_ROWS = 2
LCD_ADDRESS = 0x21

# Initialize the I2C bus and LCD once. Importing this module leaves the display
# on and ready for the application instead of running a demo and blanking it.
i2c = busio.I2C(board.SCL, board.SDA)
lcd = character_lcd.Character_LCD_I2C(i2c, LCD_COLUMNS, LCD_ROWS, LCD_ADDRESS)
lcd.backlight = True
lcd.message = "Joy-Pi ready\nWaiting for air"


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to MQTT broker: {reason_code}")
    client.subscribe("NCRasp05/sensors/air")


def on_message(client, userdata, msg):
    try:
        air = json.loads(msg.payload.decode())
        temperature = air["temperature"]
        humidity = air["humidity"]
        lcd.message = f"Temp: {temperature} C\nHumidity: {humidity}%"
    except (ValueError, KeyError, TypeError) as error:
        print(f"Invalid air reading received: {error}")


mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect("172.17.0.1", 1883, 60)
mqtt_client.loop_start()


# Keep the LCD process alive; it runs separately so Blinka's BCM GPIO mode
# cannot conflict with the sensor app's BOARD GPIO mode.
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    lcd.clear()
    lcd.backlight = False
