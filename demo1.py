import paho.mqtt.client as mqtt

# When message is received
def on_message(client, userdata, msg):
    print(f"{msg.topic}: {msg.payload.decode()}")

client = mqtt.Client()
client.connect("localhost", 1883, 60)  # Pi runs the broker

client.subscribe("esp32/#")  # Subscribe to all ESP32 topics
client.on_message = on_message

print("Listening for ESP32 messages...")
client.loop_forever()