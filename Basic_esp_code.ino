#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>

// WiFi credentials
const char* ssid = "your_ssid"; // Replace with your SSID
const char* password = "your_password"; // Replace with your Password

// Define camera pin configuration
#define CAMERA_MODEL_AI_THINKER

// Camera configuration
camera_config_t camera_config = {
  .pin_pwdn = -1,
  .pin_reset = -1,
  .pin_xclk = 19,
  .pin_siod = 21,
  .pin_sclk = 22,
  .pin_d7 = 32,
  .pin_d6 = 33,
  .pin_d5 = 25,
  .pin_d4 = 26,
  .pin_d3 = 27,
  .pin_d2 = 14,
  .pin_d1 = 12,
  .pin_d0 = 13,
  .pin_vsync = 15,
  .pin_href = 16,
  .pin_pclk = 17,
  .xclk_freq_hz = 20000000,
  .ledc_channel = 0,
  .ledc_timer = 0,
  .pixel_format = PIXFORMAT_JPEG,
  .frame_size = FRAMESIZE_SVGA,
  .jpeg_quality = 12, // 0-63 lower number means higher quality
  .fb_count = 1, // if more than one, will use extra memory
};

// Create a web server on port 80
WebServer server(80);
int currentCamera = 0; // Variable to track the active camera

void setup() {
  Serial.begin(115200);
  
  // Start the camera
  if (!startCamera()) {
    Serial.println("Camera Init Failed");
    return;
  }
  
  // Connect to WiFi
  connectToWiFi();

  // Start the web server
  server.on("/capture", HTTP_GET, handleCapture);
  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient(); // Handle incoming client requests
  delay(100); // Short delay to avoid CPU overload
}

// Function to start the camera
bool startCamera() {
  return esp_camera_init(&camera_config) == ESP_OK;
}

// Function to connect to WiFi
void connectToWiFi() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

// Function to handle image capture and serve
void handleCapture() {
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    server.send(500, "text/plain", "Camera capture failed");
    return;
  }

  // Serve the image
  server.sendHeader("Content-Type", "image/jpeg");
  server.send(fb->len, "image/jpeg", fb->buf);
  esp_camera_fb_return(fb);

  // Switch to the next camera for the next request
  currentCamera = (currentCamera + 1) % 4; // Cycle through 0 to 3
  deactivateCamera((currentCamera + 3) % 4); // Deactivate previous camera
  activateCamera(currentCamera); // Activate the next camera
}

// Function to activate camera
void activateCamera(int cam) {
  switch (cam) {
    case 0: pinMode(2, OUTPUT); digitalWrite(2, HIGH); break; // Camera 1
    case 1: pinMode(4, OUTPUT); digitalWrite(4, HIGH); break; // Camera 2
    case 2: pinMode(5, OUTPUT); digitalWrite(5, HIGH); break; // Camera 3
    case 3: pinMode(18, OUTPUT); digitalWrite(18, HIGH); break; // Camera 4
  }
}

// Function to deactivate camera
void deactivateCamera(int cam) {
  switch (cam) {
    case 0: digitalWrite(2, LOW); break; // Camera 1
    case 1: digitalWrite(4, LOW); break; // Camera 2
    case 2: digitalWrite(5, LOW); break; // Camera 3
    case 3: digitalWrite(18, LOW); break; // Camera 4
  }
}
