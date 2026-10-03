/*
 * ============================================================
 * NEXUS-PRESENCE: ESP32 #1 - MASTER NODE (VERIFIED PROTOTYPE v1)
 * Role: Wi-Fi Access Point Coordinator
 * Hardware: ESP32 DevKit v1 / ESP32-WROOM-32
 * Developed by: Uday Kiran Jammula
 * Status: TESTED & VERIFIED WORKING PROTOTYPE
 * ============================================================
 * 
 * Verified configuration:
 * SSID: NEXUS_PRESENCE
 * Password: nexus123
 * IP: 192.168.4.1
 */

#include <WiFi.h>

const char* apName = "NEXUS_PRESENCE";
const char* apPassword = "nexus123";

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("=================================");
  Serial.println("     NEXUS-PRESENCE ESP32 #1");
  Serial.println("          MASTER NODE");
  Serial.println("=================================");

  WiFi.mode(WIFI_AP);

  bool result = WiFi.softAP(apName, apPassword);

  if (result) {
    Serial.println("Access Point started!");
    Serial.print("SSID: ");
    Serial.println(apName);

    Serial.print("IP Address: ");
    Serial.println(WiFi.softAPIP());

    Serial.print("MAC Address: ");
    Serial.println(WiFi.softAPmacAddress());
  } else {
    Serial.println("Failed to start Access Point.");
  }
}

void loop() {
  int connectedDevices = WiFi.softAPgetStationNum();

  Serial.print("Connected devices: ");
  Serial.println(connectedDevices);

  delay(1000);
}
