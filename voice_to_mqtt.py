


import speech_recognition as sr
import paho.mqtt.client as mqtt
import time
import spidev

# ReSpeaker LED Controller (based on your respeaker_leds.py)
class ReSpeakerLEDs:
    def __init__(self):
        try:
            self.spi = spidev.SpiDev()
            self.spi.open(0, 0)  # bus 0, device 0
            self.spi.max_speed_hz = 8000000
            self.num_leds = 3  # ReSpeaker 2-Mics has 3 LEDs
            print("✅ ReSpeaker LEDs initialized")
        except Exception as e:
            print(f"❌ LED initialization failed: {e}")
            self.spi = None

    def set_color_all(self, red, green, blue):
        """Set all 3 LEDs to the same color"""
        if not self.spi:
            return
        try:
            # Start frame
            self.spi.xfer2([0x00, 0x00, 0x00, 0x00])
            
            # LED frames (brightness + BGR for each LED)
            brightness = 0xE0 | 0x1F  # Full brightness
            for _ in range(self.num_leds):
                self.spi.xfer2([brightness, blue, green, red])  # BGR format
            
            # End frame
            self.spi.xfer2([0xFF, 0xFF, 0xFF, 0xFF])
        except Exception as e:
            print(f"LED error: {e}")

    def turn_off(self):
        """Turn off all LEDs"""
        self.set_color_all(0, 0, 0)

# Initialize LED controller
leds = ReSpeakerLEDs()

def set_led(color):
    if color == 'listening':
        leds.set_color_all(0, 0, 255)  # Blue
    elif color == 'recognized':
        leds.set_color_all(0, 255, 0)  # Green
    elif color == 'sent':
        leds.set_color_all(255, 0, 0)  # Red
    elif color == 'error':
        leds.set_color_all(255, 255, 0)  # Yellow
    else:
        leds.turn_off()

import speech_recognition as sr
import paho.mqtt.client as mqtt

MQTT_BROKER = "10.136.186.56"  # Your Pi's IP
MQTT_TOPIC = "servo/control"


def send_mqtt_command(command):
    client = mqtt.Client()
    client.connect(MQTT_BROKER, 1883, 60)
    client.publish(MQTT_TOPIC, command)
    client.disconnect()
    print(f"Sent MQTT: {command}")
    set_led('sent')



recognizer = sr.Recognizer()
mic = sr.Microphone()

print("Say 'open' or 'close' to control the servo.")

# Startup LED pulse for confirmation
set_led('listening')
time.sleep(0.5)
set_led('off')

while True:
    with mic as source:
        set_led('listening')
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)
        except Exception as e:
            print(f"Listen error: {e}")
            set_led('error')
            time.sleep(0.5)
            continue
    try:
        set_led('recognized')
        text = recognizer.recognize_google(audio).lower()
        print(f"You said: {text}")
        if "open" in text:
            send_mqtt_command("open")
        elif "close" in text:
            send_mqtt_command("close")
    except sr.UnknownValueError:
        print("Could not understand audio")
        set_led('error')
        time.sleep(0.5)
    except Exception as e:
        print(f"Error: {e}")
        set_led('error')
        time.sleep(0.5)