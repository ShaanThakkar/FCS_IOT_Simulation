import paho.mqtt.client as mqtt
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from xtea import new as xtea_new, MODE_CBC
import time

MQTT_BROKER = "broker.hivemq.com"  # Use public MQTT broker
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

def main():
    client = mqtt.Client(client_id="DeviceA", protocol=mqtt.MQTTv311)
    client.connect(MQTT_BROKER)
    print(f"[Device A] Connected to MQTT broker at {MQTT_BROKER}")
    print(f"Encryption mode: {mode}")
    print("Type a message and press Enter to send it. Type 'exit' to quit.\n")
    while True:
        user_input = input("Enter message to send: ")
        if user_input.strip().lower() == "exit":
            print("[Device A] Sending shutdown signal to Device B...")
            client.publish(TOPIC, "::shutdown::")
            time.sleep(1)
            print("[Device A] Exiting.")
            break
        encrypted_msg, time_taken = encrypt_message(user_input)
        print(f"[Device A] Encrypted in {time_taken:.3f} ms")
        client.publish(TOPIC, encrypted_msg)
        print(f"[Device A] Sent (encrypted): {encrypted_msg}\n")
    client.disconnect()

if __name__ == "__main__":
    main()
