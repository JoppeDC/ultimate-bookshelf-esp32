#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <ArduinoJson.h>
#include <FastLED.h>
#include "config.h"
#include "secrets.h"

CRGB leds[NUM_LEDS];
AsyncWebServer server(80);

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS);
  FastLED.clear(true);

  server.on("/set_all", HTTP_POST, [](AsyncWebServerRequest *request){}, NULL,
    [](AsyncWebServerRequest *request, uint8_t *data, size_t len, size_t, size_t) {
      DynamicJsonDocument doc(512);
      deserializeJson(doc, data);
      int r = doc["r"];
      int g = doc["g"];
      int b = doc["b"];
      int a = doc["a"];
      Serial.printf("Set ALL LEDs to RGB(%d,%d,%d) with %d%% opacity\n", r, g, b, a);

      CRGB color = CRGB(r, g, b).nscale8(map(a, 0, 100, 0, 255));
      fill_solid(leds, NUM_LEDS, color);
      FastLED.show();

      request->send(200, "application/json", "{\"status\":\"ok\"}");
    });

  server.on("/set_led", HTTP_POST, [](AsyncWebServerRequest *request){}, NULL,
    [](AsyncWebServerRequest *request, uint8_t *data, size_t len, size_t, size_t) {
      DynamicJsonDocument doc(2048);
      DeserializationError error = deserializeJson(doc, data);

      if (error) {
        request->send(400, "application/json", "{\"error\":\"Invalid JSON\"}");
        return;
      }

      if (!doc.is<JsonArray>()) {
        request->send(400, "application/json", "{\"error\":\"Expected JSON array\"}");
        return;
      }

      for (JsonObject obj : doc.as<JsonArray>()) {
        int led = obj["led"] | -1;
        int r = obj["r"] | 0;
        int g = obj["g"] | 0;
        int b = obj["b"] | 0;
        int a = obj["a"] | 100;

        if (led < 0 || led >= NUM_LEDS) {
          Serial.println("Invalid LED index.");
          continue;
        }

        Serial.printf("LED %d → RGB(%d,%d,%d) @ %d%% opacity\n", led, r, g, b, a);
        leds[led] = CRGB(r, g, b).nscale8(map(a, 0, 100, 0, 255));
      }

      FastLED.show();
      
      request->send(200, "application/json", "{\"status\":\"batch ok\"}");
    }
  );

  server.begin();
}

void loop() {}
