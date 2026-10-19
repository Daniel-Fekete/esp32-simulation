import json
import math
import os
import random
import threading
import time

import paho.mqtt.client as mqtt


MQTT_HOST = os.getenv("MQTT_HOST", "mqtt")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.environ["MQTT_TOPIC"]
INTERVAL = float(os.getenv("SENSOR_INTERVAL_SECONDS", "5"))

if INTERVAL <= 0:
    raise ValueError("SENSOR_INTERVAL_SECONDS must be greater than zero")

connected = threading.Event()


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        connected.set()
        print(f"Connected to MQTT: {MQTT_HOST}:{MQTT_PORT}", flush=True)
    else:
        connected.clear()
        print(f"MQTT connection rejected: {reason_code}", flush=True)


def on_disconnect(client, userdata, flags, reason_code, properties):
    connected.clear()
    print(f"MQTT disconnected: {reason_code}", flush=True)


client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id="fekdac22-esp32-simulator",
)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.reconnect_delay_set(min_delay=1, max_delay=30)

client.connect_async(MQTT_HOST, MQTT_PORT, keepalive=60)
client.loop_start()

started = time.monotonic()

try:
    while True:
        if not connected.wait(timeout=5):
            print("Waiting for MQTT broker...", flush=True)
            continue

        elapsed = time.monotonic() - started

        reading = {
            "device": "esp32-sim",
            "timestamp": int(time.time()),
            "temperature": round(
                22 + 2 * math.sin(elapsed / 60) + random.uniform(-0.3, 0.3),
                2,
            ),
            "humidity": round(
                50 + 5 * math.sin(elapsed / 90) + random.uniform(-1, 1),
                2,
            ),
        }

        payload = json.dumps(reading)

        try:
            result = client.publish(
                MQTT_TOPIC,
                payload=payload,
                qos=1,
                retain=False,
            )
            result.wait_for_publish(timeout=10)

            if result.is_published():
                print(f"{MQTT_TOPIC}: {payload}", flush=True)
            else:
                print("Publish acknowledgement timed out", flush=True)
        except (RuntimeError, ValueError) as error:
            print(f"Publish failed: {error}", flush=True)

        time.sleep(INTERVAL)
finally:
    client.disconnect()
    client.loop_stop()
