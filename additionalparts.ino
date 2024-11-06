#include <SPI.h>
#include <MFRC522.h>

// RFID pins
#define SS_PIN 10  // SDA
#define RST_PIN 9  // RST

// Ultrasonic sensor pins
#define TRIG_PIN 7
#define ECHO_PIN 6

// Magnetic float sensor pin
#define FLOAT_SENSOR_PIN 5

// Relay control pin for pump
#define RELAY_PIN 4

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance

void setup() {
  Serial.begin(9600);   // Initialize serial communications with the PC
  SPI.begin();          // Initialize SPI bus
  mfrc522.PCD_Init();   // Initialize the RFID reader

  // Initialize the ultrasonic sensor
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // Initialize the float sensor and relay control pin
  pinMode(FLOAT_SENSOR_PIN, INPUT_PULLUP);  // Enable internal pull-up resistor
  pinMode(RELAY_PIN, OUTPUT);
  
  Serial.println("Place your RFID tag near the reader...");
}

void loop() {
  // Look for new cards
  if (!mfrc522.PICC_IsNewCardPresent()) {
    return;
  }

  // Select one of the cards
  if (!mfrc522.PICC_ReadCardSerial()) {
    return;
  }

  // Show UID on the serial monitor
  Serial.print("UID tag: ");
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
    Serial.print(mfrc522.uid.uidByte[i], HEX);
  }
  Serial.println();

  // Check for an object using the ultrasonic sensor
  long distance = getDistance();
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  // If the object is detected (e.g., distance is less than 10 cm), trigger the signal for 10 seconds
  if (distance < 10) {
    Serial.println("Object detected! Sending signal for 10 seconds...");
    sendSignal(10);  // Send signal for 10 seconds
  }

  // Read the float sensor to check water level
  int floatSensorState = digitalRead(FLOAT_SENSOR_PIN);
  
  // If the water level is high (sensor triggered), turn on the pump
  if (floatSensorState == LOW) {  // Reed switch is closed when triggered (water level high)
    Serial.println("Water level high. Turning on the pump.");
    digitalWrite(RELAY_PIN, HIGH);  // Turn on pump
  } else {
    Serial.println("Water level low. Turning off the pump.");
    digitalWrite(RELAY_PIN, LOW);   // Turn off pump
  }

  delay(1000);  // Add delay to avoid constant reading
}

// Function to get distance from ultrasonic sensor
long getDistance() {
  // Send a pulse to the TRIG pin to start measurement
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // Measure the pulse width on the ECHO pin
  long duration = pulseIn(ECHO_PIN, HIGH);

  // Calculate the distance in cm (speed of sound = 34300 cm/s)
  long distance = duration * 0.0344 / 2;
  return distance;
}

// Function to send signal for a specified duration
void sendSignal(int duration) {
  long startTime = millis();  // Record the start time

  while (millis() - startTime < duration * 1000) {
    // Here, you can trigger any signal, for example, turning on an LED or a buzzer.
    // Example: Turn on an LED on pin 8 during this period.
    pinMode(8, OUTPUT);
    digitalWrite(8, HIGH);
  }

  // Turn off the signal after 10 seconds
  digitalWrite(8, LOW);
}
