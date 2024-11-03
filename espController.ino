#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <OV7670.h>

const char *ssid = "YourSSID";
const char *password = "YourPassword";

AsyncWebServer server(80);
OV7670 camera[4]; // Array of 4 camera objects

// Array to store the latest vehicle counts for each road
int vehicleCounts[4] = {0, 0, 0, 0};

void setup()
{
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Initialize each camera
  for (int i = 0; i < 4; i++)
  {
    camera[i].init();
  }

  // Capture endpoint for each camera
  for (int i = 0; i < 4; i++)
  {
    server.on(String("/capture") + i, HTTP_GET, [i](AsyncWebServerRequest *request)
              {
            camera[i].capture();
            request->send_P(200, "image/jpeg", camera[i].getJPEGBuffer(), camera[i].getJPEGBufferSize()); });
  }

  // Endpoint to update vehicle counts
  server.on("/update_counts", HTTP_POST, [](AsyncWebServerRequest *request)
            {
        if (request->hasParam("R1", true) && request->hasParam("R2", true) &&
            request->hasParam("R3", true) && request->hasParam("R4", true)) {
            
            vehicleCounts[0] = request->getParam("R1", true)->value().toInt();
            vehicleCounts[1] = request->getParam("R2", true)->value().toInt();
            vehicleCounts[2] = request->getParam("R3", true)->value().toInt();
            vehicleCounts[3] = request->getParam("R4", true)->value().toInt();

            Serial.println("Vehicle counts updated!");
            request->send(200, "text/plain", "Counts updated");
        } else {
            request->send(400, "text/plain", "Invalid parameters");
        } });

  // Endpoint to retrieve the latest vehicle counts
  server.on("/vehicle_counts", HTTP_GET, [](AsyncWebServerRequest *request)
            {
        String response = String("R1:") + vehicleCounts[0] + 
                          ",R2:" + vehicleCounts[1] + 
                          ",R3:" + vehicleCounts[2] + 
                          ",R4:" + vehicleCounts[3];
        request->send(200, "text/plain", response); });

  server.begin();
}

void loop()
{
  // Empty loop - server runs asynchronously
}
