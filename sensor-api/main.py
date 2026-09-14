from http.server import BaseHTTPRequestHandler, HTTPServer
from time import sleep
from air_sensor import AirSensor
from light_sensor import LightSensor
from sound_sensor import SoundSensor
import mimetypes
import json
import os
import textwrap

air_sensor = AirSensor()
light_sensor = LightSensor()
sound_sensor = SoundSensor()

host = "0.0.0.0"
port = 8080

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
            sound_val = 1 if sound.get("sound_detected") else 0

            response = textwrap.dedent(f"""
                # HELP sensor_light measured light itensity in lux\n\
                # TYPE sensor_light gauge\n\
                sensor_light {light}\n\
                # HELP sensor_air_temperature measured temperature in celcius\n\
                # TYPE sensor_air_temperature gauge\n\
                sensor_air_temperature {air.temperature}\n\
                # HELP sensor_air_humidity measured humidity in percent\n\
                # TYPE sensor_air_humidity gauge\n\
                sensor_air_humidity {air.humidity}
                # HELP sensor_sound_detected binary sound detection flag (1 or 0)
                # TYPE sensor_sound_detected gauge
                sensor_sound_detected {sound_val}
            """)

            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "*")
            self.send_header("Access-Control-Allow-Headers", "*")
            self.send_header("Vary", "Origin")
            self.send_header("Content-type", "text/plain")
            self.end_headers()

            self.wfile.write(response.encode())


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


def main():
    web_server = HTTPServer((host, port), Server)
    print(f"Server started and listen to {host}:{port}")

    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

print("Server stopped")
 