#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <OV7670.h>
#include <HTTPClient.h>

const char *ssid = "YourSSID";
const char *password = "YourPassword";
const char *pythonServerUrl = "http://<your_python_server_ip>:<your_port>/process_image"; // Replace with your Python server URL

AsyncWebServer server(80);

// Camera configuration
OV7670 camera;  // Single camera object to share among all cameras
int powerPins[] = {2, 4, 5, 18};  // Power control pins for each camera
int activeCamera = -1;  // Current active camera
int vehicleCount = 0;   // Variable to store the count of vehicles detected

void setup() {
    Serial.begin(115200);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to WiFi");

    // Initialize power pins
    for (int i = 0; i < 4; i++) {
        pinMode(powerPins[i], OUTPUT);
        digitalWrite(powerPins[i], LOW);  // All cameras off initially
    }

    // Camera capture endpoint for each camera
    for (int i = 0; i < 4; i++) {
        server.on(String("/capture") + i, HTTP_GET, [i](AsyncWebServerRequest *request) {
            switchCamera(i);  // Activate selected camera
            delay(100);  // Give camera time to power up
            camera.capture();

            // Send image to Python server and get vehicle count
            vehicleCount = sendImageToServer(camera.getJPEGBuffer(), camera.getJPEGBufferSize());
            
            request->send_P(200, "image/jpeg", camera.getJPEGBuffer(), camera.getJPEGBufferSize());
            delay(100);  // Allow capture to finish before switching
            deactivateCamera();  // Turn off the current camera

            Serial.printf("Vehicle count from server: %d\n", vehicleCount);
        });
    }

    server.begin();
}

void switchCamera(int cameraId) {
    deactivateCamera();  // Deactivate any currently active camera
    activeCamera = cameraId;
    digitalWrite(powerPins[cameraId], HIGH);  // Power on the selected camera
    Serial.printf("Camera %d activated\n", cameraId);
}

void deactivateCamera() {
    if (activeCamera != -1) {
        digitalWrite(powerPins[activeCamera], LOW);  // Turn off active camera
        Serial.printf("Camera %d deactivated\n", activeCamera);
        activeCamera = -1;
    }
}

int sendImageToServer(uint8_t *imageBuffer, size_t imageSize) {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(pythonServerUrl);
        http.addHeader("Content-Type", "application/octet-stream");

        int httpResponseCode = http.POST((uint8_t *)imageBuffer, imageSize);
        if (httpResponseCode > 0) {
            String response = http.getString();
            Serial.printf("Image sent to server, response code: %d\n", httpResponseCode);
            http.end();

            // Parse the response to extract vehicle count
            return response.toInt(); // Return the vehicle count as an integer
        } else {
            Serial.printf("Error sending image: %s\n", http.errorToString(httpResponseCode).c_str());
            http.end();
        }
    } else {
        Serial.println("WiFi not connected");
    }
    return -1;  // Return -1 in case of an error
}

void loop() {
    // Empty loop, server runs asynchronously
}
