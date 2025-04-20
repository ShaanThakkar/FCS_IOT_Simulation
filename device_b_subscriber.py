import paho.mqtt.client as mqtt
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from xtea import new as xtea_new, MODE_CBC
import time

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
    decrypted_text = decrypted.decode()
    return decrypted_text, elapsed

def on_message(client, userdata, message):
    print(f"\n[Device B] Encrypted Message Received: {message.payload}")
    try:
        decrypted, time_taken = decrypt_message(message.payload)
        if decrypted.strip() == "::shutdown::":
            print("[Device B] Shutdown signal received. Exiting...\n")
            client.disconnect()
            exit(0)
        print(f"[Device B] Decrypted in {time_taken:.3f} ms")
        print(f"[Device B] Message: {decrypted}")
    except Exception as e:
        print(f"[Device B] ERROR: {e}")

client = mqtt.Client(client_id="DeviceB", protocol=mqtt.MQTTv311)
client.connect(MQTT_BROKER)
client.subscribe(TOPIC)
client.on_message = on_message
print("[Device B] Listening for messages...\n")
client.loop_forever()
