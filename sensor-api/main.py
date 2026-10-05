from http.server import BaseHTTPRequestHandler, HTTPServer
from time import sleep
from air_sensor import AirSensor
from light_sensor import LightSensor
from motion_sensor import MotionSensor
from sound_sensor import SoundSensor
from distance_sensor import DistanceSensor
from touch_sensor import TouchSensor
import mimetypes
import threading
import json
import os
import textwrap

import paho.mqtt.client as mqtt

air_sensor = AirSensor()
light_sensor = LightSensor()
sound_sensor = SoundSensor()
distance_sensor = DistanceSensor()
motion_sensor = MotionSensor()
touch_sensor = TouchSensor(11)
touch_count = 0

host = "0.0.0.0"
port = 8080


def on_connect(client, userdata, flags, reason_code, properites):
    print(f"Connected to MQTT Broker with result {reason_code}")


def on_message(client, userdata, msg: object):
    print(msg.topic + " " + str(msg.payload))


mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect("172.17.0.1", 1883, 60)

sleep(1)


class Server(BaseHTTPRequestHandler):
    def sendJSON(self, object: object, code: int = 200):
        self.send_response(code)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Vary", "Origin")
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(object).encode())

    def serveStatic(self):
        local_file_path = os.path.join(".", self.path[1:], "index.html")
        print(local_file_path)

        if os.path.exists(local_file_path) and os.path.isfile(local_file_path):
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "*")
            self.send_header("Access-Control-Allow-Headers", "*")
            self.send_header("Vary", "Origin")

            mime_type, _ = mimetypes.guess_type(local_file_path)
            if mime_type:
                self.send_header("Content-type", mime_type)
            else:
                self.send_header("Content-type", "application/octet-stream")

            self.end_headers()

            with open(local_file_path, "rb") as file:
                self.wfile.write(file.read())

    def do_GET(self):
        if self.path == "/":
            self.serveStatic()

        if self.path == "/metrics":
            air = air_sensor.readAir()
            light = light_sensor.readLight()
            sound = sound_sensor.readSound()
            motion = motion_sensor.readMotion()
            touch = touch_sensor.readTouch()
            distance = distance_sensor.read()

            #Better metrics page with HTML template rendering
            with open("metrics.html", "r", encoding="utf-8") as f:
                html = f.read()

            html = (
                html.replace("{temperature}", str(air.temperature))
                .replace("{humidity}", str(air.humidity))
                .replace("{light}", str(light))
                .replace(
                    "{distance}",
                    f"{distance} cm" if distance != -1 else "Außer Reichweite",
                )
                .replace(
                    "{sound}", "Ja" if sound.get("sound_detected") else "Nein"
                )
                .replace(
                    "{motion}", "Ja" if motion.get("motion_detected") else "Nein"
                )
                .replace("{touch}", "Nein" if touch else "Ja")
            )

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))

        if self.path == "/api/air":
            air = air_sensor.readAir()
            self.sendJSON(
                {
                    "status": "ok",
                    "data": [
                        {
                            "label": "Temperature",
                            "value": air.temperature,
                            "unit": "°C",
                        },
                        {"label": "Humidity", "value": air.humidity, "unit": "%"},
                    ],
                }
            )

        if self.path == "/api/light":
            self.sendJSON(
                {
                    "status": "ok",
                    "data": {
                        "label": "Illuminance",
                        "value": light_sensor.readLight(),
                        "unit": "lux",
                    },
                }
            )

        if self.path == "/api/sound":
            sound = sound_sensor.readSound()
            self.sendJSON(
                {
                    "status": "ok",
                    "data": {
                        "label": "Sound Detected",
                        "value": sound.get("sound_detected", False),
                        "unit": "boolean",
                    },
                }
            )


def read_distance_sensor(delay):
    while True:
        distance = distance_sensor.read()
        mqtt_client.publish("NCRasp05/sensor/distance", distance, qos=2)
        sleep(delay)


def publish_air_readings(delay=2):
    while True:
        air = air_sensor.readAir()
        if air and air.is_valid():
            mqtt_client.publish(
                "NCRasp05/sensors/air",
                json.dumps({"temperature": air.temperature, "humidity": air.humidity}),
                qos=1,
                retain=True,
            )
        sleep(delay)


def handle_touch(is_touched):
    global touch_count
    is_touched = not is_touched
    mqtt_client.publish("NCRasp05/sensor/touch/active", is_touched, qos=2)
    if is_touched:
        touch_count += 1
        print("Touch Detected!")
        mqtt_client.publish("NCRasp05/sensor/touch/count", touch_count, qos=2)


def main():
    web_server = HTTPServer((host, port), Server)
    print(f"Server started and listen to {host}:{port}")

    distanceSensorThread = threading.Thread(
        target=read_distance_sensor, args=(0.3,), daemon=True
    )

    distanceSensorThread.start()

    airSensorThread = threading.Thread(target=publish_air_readings, daemon=True)
    airSensorThread.start()

    touch_sensor.start(handle_touch)

    try:
        mqtt_client.loop_start()
        mqtt_client.publish("NCRasp05/up", "true", qos=2)
        web_server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

print("Server stopped")
