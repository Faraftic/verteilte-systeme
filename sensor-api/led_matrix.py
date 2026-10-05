import os
import queue
import time
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.legacy import show_message
from luma.core.legacy.font import proportional, CP437_FONT
import paho.mqtt.client as mqtt

MESSAGE_TOPIC = "NCRasp05/matrix/message"
messages = queue.Queue()


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to MQTT broker: {reason_code}")
    client.subscribe(MESSAGE_TOPIC)


def on_message(client, userdata, message):
    text = message.payload.decode("utf-8", errors="replace").strip()
    if text:
        messages.put(text[:200])


def main(cascaded, block_orientation, rotate):

    # create and set matrix device
    serial = spi(port=0, device=1, gpio=noop())
    device = max7219(
        serial,
        cascaded=cascaded or 1,
        block_orientation=block_orientation,
        rotate=rotate or 0,
    )
    # display initilisation of matrix in console
    print("[-] Matrix initialized")

    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(os.getenv("MQTT_HOST", "172.17.0.1"), 1883, 60)
    mqtt_client.loop_start()

    print(f"[-] Waiting for messages on {MESSAGE_TOPIC}")
    while True:
        msg = messages.get()
        print(f"[-] Printing: {msg}")
        show_message(
            device, msg, fill="white", font=proportional(CP437_FONT), scroll_delay=0.1
        )


if __name__ == "__main__":

    # cascaded = Number of cascaded MAX7219 LED matrices, default = 1
    # block_orientation = choices 0, 90, -90, default = 0
    # rotate = choices 0, 1, 2, 3, Rotate display 0=0°, 1=90°, 2=180°, 3=270°, default = 0

    try:
        main(cascaded=1, block_orientation=90, rotate=0)
    except KeyboardInterrupt:
        pass
