from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from air_sensor import AirSensor
from light_sensor import LightSensor
import paho.mqtt.client as mqtt

air_sensor = AirSensor()
light_sensor = LightSensor()

host = "0.0.0.0"
port = 5000  # Port 5000 laut Aufgabenstellung

KOFFER_NR = "N05"
MQTT_TOPIC = f"raspi/{KOFFER_NR}/http/request"

def on_connect(client, userdata, flags, reason_code, properites):
    print(f"Connected to MQTT Broker with result {reason_code}")


def on_message(client, userdata, msg: object):
    print(msg.topic + " " + str(msg.payload))

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect("10.5.61.199", 1883, 60)


class Server(BaseHTTPRequestHandler):

    def sendJSON(self, data: object, code: int = 200):
        self.send_response(code)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_GET(self):

        payload = json.dumps({"path": self.path, "method": self.command})
        mqtt_client.publish(MQTT_TOPIC, payload, qos=0, retain=False)

        # /api/sensors auf gleicher Ebene wie andere Pfade prüfen!
        if self.path == "/api/sensors":
            air = air_sensor.readAir()

            # Auslesen der Werte mit Absicherung gegen None-Werte beim Start
            temp_value = air.temperature if air else None
            humidity_value = air.humidity if air else None
            light_value = light_sensor.readLight()

            self.sendJSON(
                {
                    "status": "ok",
                    "data": [
                        {
                            "label": "Illuminance",
                            "value": light_value,
                            "unit": "lux",
                        },
                        {
                            "label": "Temperature",
                            "value": temp_value,
                            "unit": "°C",
                        },
                        {
                            "label": "Humidity",
                            "value": humidity_value,
                            "unit": "%",
                        },
                    ],
                }
            )
        else:
            self.sendJSON({"error": "Not Found"}, 404)


def main():
    web_server = HTTPServer((host, port), Server)
    print(f"Server gestartet unter http://{host}:{port}/api/sensors")

    try:
        mqtt_client.loop_start()
        web_server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()