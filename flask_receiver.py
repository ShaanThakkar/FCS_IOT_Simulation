from flask import Flask, Response, render_template_string
import paho.mqtt.client as mqtt
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from xtea import new as xtea_new, MODE_CBC
import time
import queue
import threading
import os

app = Flask(__name__)
msg_queue = queue.Queue()

aes_key = b'Sixteen byte key'
xtea_key = b'16bytesSecretKey'
aes_iv = b'0123456789abcdef'
xtea_iv = b'ABCDEFGH'
mode = "AES"
MQTT_BROKER = "broker.hivemq.com"
TOPIC = "iot/simulation/topic"

def decrypt_message(data: bytes):
    start = time.perf_counter()
    if mode == "AES":
        cipher = AES.new(aes_key, AES.MODE_CBC, iv=aes_iv)
        decrypted = unpad(cipher.decrypt(data), AES.block_size)
    elif mode == "XTEA":
        cipher = xtea_new(xtea_key, mode=MODE_CBC, IV=xtea_iv)
        decrypted = unpad(cipher.decrypt(data), 8)
    else:
        decrypted = data
    elapsed = (time.perf_counter() - start) * 1000
    return decrypted.decode(), elapsed

def mqtt_listener():
    def on_message(client, userdata, message):
        try:
            decrypted, time_taken = decrypt_message(message.payload)
            output = f"[{time_taken:.2f} ms] {decrypted}"
            msg_queue.put(output)
        except Exception as e:
            msg_queue.put(f"Decryption error: {e}")

    client = mqtt.Client(client_id="DeviceB_UI", protocol=mqtt.MQTTv311)
    client.connect(MQTT_BROKER)
    client.subscribe(TOPIC)
    client.on_message = on_message
    client.loop_forever()

@app.route("/")
def index():
    return render_template_string(open("device_b_ui.html").read())

@app.route("/stream")
def stream():
    def event_stream():
        while True:
            message = msg_queue.get()
            yield f"data: {message}\n\n"
    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == "__main__":
    threading.Thread(target=mqtt_listener, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
