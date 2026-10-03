/*
 * ============================================================
 * NEXUS-PRESENCE: ESP32 #2 - SENSOR NODE (VERIFIED PROTOTYPE v1)
 * Role: Wi-Fi Station RSSI Collector
 * Hardware: ESP32 DevKit v1 / ESP32-WROOM-32
 * Developed by: Uday Kiran Jammula
 * Status: TESTED & VERIFIED WORKING PROTOTYPE
 * ============================================================
 * 
 * Target AP: NEXUS_PRESENCE
 * Password: nexus123
 */

#include <WiFi.h>

const char* ssid = "NEXUS_PRESENCE";
const char* password = "nexus123";

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("=================================");
  Serial.println("     NEXUS-PRESENCE ESP32 #2");
  Serial.println("          SENSOR NODE");
  Serial.println("=================================");

  WiFi.mode(WIFI_STA);

  Serial.print("Connecting");

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("Connected!");

  Serial.print("ESP32 #2 IP: ");
  Serial.println(WiFi.localIP());

  Serial.print("Signal strength: ");
  Serial.print(WiFi.RSSI());
  Serial.println(" dBm");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    long rssi = WiFi.RSSI();

    Serial.print("RSSI: ");
    Serial.print(rssi);
    Serial.println(" dBm");
  } else {
    Serial.println("Connection lost!");
    WiFi.begin(ssid, password);
  }

  delay(250);
}
