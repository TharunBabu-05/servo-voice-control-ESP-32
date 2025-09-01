#include <WiFi.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>

// Wi-Fi credentials
const char* ssid = "Jack's";
const char* password = "10101010.";

// MQTT broker (Raspberry Pi IP)
const char* mqtt_server = "10.136.186.56";

WiFiClient espClient;
PubSubClient client(espClient);

Servo myservo;
const int servoPin = 13;

// Current servo position tracking
int currentAngle = 90; // Start at center

void set_angle(int angle) {
  if (angle < 0) angle = 0;
  if (angle > 180) angle = 180;
  
  myservo.write(angle);
  currentAngle = angle;
  delay(100); // Short delay for smoother movement
  Serial.println("Servo moved to " + String(angle) + " degrees");
}

void dance_routine() {
  Serial.println("🕺 Starting dance routine!");
  
  // Quick sweep back & forth
  for (int i = 0; i < 3; i++) {
    for (int angle = 0; angle <= 180; angle += 30) {
      set_angle(angle);
      delay(50);
    }
    for (int angle = 180; angle >= 0; angle -= 30) {
      set_angle(angle);
      delay(50);
    }
  }
  
  // Fast wiggle around center
  for (int i = 0; i < 5; i++) {
    set_angle(60);
    delay(50);
    set_angle(120);
    delay(50);
  }
  
  // Return to center
  set_angle(90);
  Serial.println("🎉 Dance complete!");
}

void callback(char* topic, byte* message, unsigned int length) {
  String msg;
  for (unsigned int i = 0; i < length; i++) {
    msg += (char)message[i];
  }
  
  Serial.println("Received: " + msg);
  
  // Basic commands
  if (msg == "open") {
    set_angle(90); // Open position
  } 
  else if (msg == "close") {
    set_angle(0); // Close position
  }
  
  // Angle commands
  else if (msg == "30_right") {
    set_angle(currentAngle + 30);
  }
  else if (msg == "30_left") {
    set_angle(currentAngle - 30);
  }
  else if (msg == "90_right") {
    set_angle(currentAngle + 90);
  }
  else if (msg == "90_left") {
    set_angle(currentAngle - 90);
  }
  else if (msg == "180_right") {
    set_angle(180); // Full right
  }
  else if (msg == "180_left") {
    set_angle(0); // Full left
  }
  
  // Dance command
  else if (msg == "dance") {
    dance_routine();
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32ServoClient")) {
      Serial.println("connected");
      client.subscribe("servo/control");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  myservo.attach(servoPin);
  myservo.write(90); // Start at center

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");

  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}
