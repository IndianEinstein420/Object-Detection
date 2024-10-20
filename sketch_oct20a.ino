void setup() {
  Serial.begin(9600);  // Set the baud rate to match Python's
  pinMode(1, OUTPUT);
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(12, OUTPUT);
  digitalWrite(1,HIGH);
  digitalWrite(4,HIGH);
  digitalWrite(7,HIGH);
  digitalWrite(10,HIGH);
}

void loop() {
  if (Serial.available()) {
    String vehicle_data = Serial.readStringUntil('\n');  // Read incoming data
    Serial.println("Received data: " + vehicle_data);  // Print it for debugging
    
    // You can now use the vehicle_data for further processing, such as controlling LEDs or motors.
    delay(500);
    digitalWrite(1,LOW);
    digitalWrite(2,HIGH);
    delay(1000);
    digitalWrite(2,LOW);
    digitalWrite(3,HIGH);
    delay(1000);
    digitalWrite(3,LOW);
    digitalWrite(1,HIGH);
    digitalWrite(4,LOW);
    digitalWrite(5,HIGH);
    delay(1000);
    digitalWrite(5,LOW);
    digitalWrite(6,HIGH);
    delay(1000);
    digitalWrite(6,LOW);
    digitalWrite(4,HIGH);
    digitalWrite(7,LOW);
    digitalWrite(8,HIGH);
    delay(1000);
    digitalWrite(8,LOW);
    digitalWrite(9,HIGH);
    delay(1000);
    digitalWrite(9,LOW);
    digitalWrite(7,HIGH);
    digitalWrite(10,LOW);
    digitalWrite(11,HIGH);
    delay(1000);
    digitalWrite(11,LOW);
    digitalWrite(12,HIGH);
    delay(1000);
    digitalWrite(12,LOW);
    digitalWrite(10,HIGH);
    delay(500);
  }
  else{
    Serial.println("Serial not found");
  }
}
