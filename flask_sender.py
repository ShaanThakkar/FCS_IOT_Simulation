from flask import Flask, request, render_template_string
import paho.mqtt.client as mqtt
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from xtea import new as xtea_new, MODE_CBC
import time
import os

app = Flask(__name__)

MQTT_BROKER = "broker.hivemq.com"
TOPIC = "iot/simulation/topic"
aes_key = b'Sixteen byte key'
xtea_key = b'16bytesSecretKey'
aes_iv = b'0123456789abcdef'
xtea_iv = b'ABCDEFGH'
mode = "AES"

def encrypt_message(msg: str):
    data = msg.encode()
    start = time.perf_counter()
    if mode == "AES":
        cipher = AES.new(aes_key, AES.MODE_CBC, iv=aes_iv)
        encrypted = cipher.encrypt(pad(data, AES.block_size))
    elif mode == "XTEA":
        cipher = xtea_new(xtea_key, mode=MODE_CBC, IV=xtea_iv)
        encrypted = cipher.encrypt(pad(data, 8))
    else:
        encrypted = data
    elapsed = (time.perf_counter() - start) * 1000
    return encrypted, elapsed

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        msg = request.form.get("message")
        if msg:
            encrypted, time_taken = encrypt_message(msg)
            client = mqtt.Client(client_id="FlaskDeviceA", protocol=mqtt.MQTTv311)
            client.connect(MQTT_BROKER)
            client.publish(TOPIC, encrypted)
            client.disconnect()
            result = f"Encrypted & sent in {time_taken:.3f} ms"
    return render_template_string(open("device_a_ui.html").read(), result=result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
