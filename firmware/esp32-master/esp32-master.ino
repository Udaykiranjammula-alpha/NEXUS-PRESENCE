/*
 * ============================================================
 * NEXUS-PRESENCE: ESP32 #1 - PRODUCTION MASTER COORDINATOR
 * Project: Multi-Node Ambient Wi-Fi Human Presence System
 * Author: Uday Kiran Jammula
 * 
 * Hardware: ESP32 DevKit v1 / ESP32-WROOM-32
 * Role: Wi-Fi SoftAP Gateway & UDP Telemetry Aggregator
 * ============================================================
 */

#include <WiFi.h>
#include <WiFiUdp.h>

// Configurable Parameters
const char* AP_SSID = "NEXUS_PRESENCE";
const char* AP_PASS = "nexus123";
const IPAddress AP_IP(192, 168, 4, 1);
const IPAddress AP_GATEWAY(192, 168, 4, 1);
const IPAddress AP_SUBNET(255, 255, 255, 0);
const uint16_t UDP_PORT = 5005;

WiFiUDP udp;
uint32_t totalPacketsAggregated = 0;
unsigned long lastHeartbeat = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("==================================================");
  Serial.println("         NEXUS-PRESENCE: MASTER NODE #1           ");
  Serial.println("      Wi-Fi Ambient RF Gateway & Aggregator       ");
  Serial.println("            Author: Uday Kiran Jammula            ");
  Serial.println("==================================================");

  // Configure SoftAP
  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(AP_IP, AP_GATEWAY, AP_SUBNET);
  bool apSuccess = WiFi.softAP(AP_SSID, AP_PASS, 6, 0, 4); // Channel 6, max 4 stations

  if (apSuccess) {
    Serial.println("[AP] Access Point started successfully.");
    Serial.print("[AP] SSID:        "); Serial.println(AP_SSID);
    Serial.print("[AP] Gateway IP:  "); Serial.println(WiFi.softAPIP());
    Serial.print("[AP] MAC Address: "); Serial.println(WiFi.softAPmacAddress());
    Serial.print("[AP] Channel:     6 (2.437 GHz)\n");
  } else {
    Serial.println("[AP] ERROR: Failed to start SoftAP!");
  }

  // Start UDP Listener for Node Telemetry
  udp.begin(UDP_PORT);
  Serial.print("[UDP] Listening for sensor telemetry on port ");
  Serial.println(UDP_PORT);
  Serial.println("[SYSTEM] Ready. Telemetry stream starting...\n");
}

void loop() {
  // Check for incoming UDP telemetry packets from Sensor Nodes #2, #3, #4
  int packetSize = udp.parsePacket();
  if (packetSize > 0) {
    char packetBuffer[512];
    int len = udp.read(packetBuffer, sizeof(packetBuffer) - 1);
    if (len > 0) {
      packetBuffer[len] = '\0';
      totalPacketsAggregated++;

      // Forward directly over high-speed Serial to Python backend
      Serial.println(packetBuffer);
    }
  }

  // Periodic Gateway Heartbeat / Master Node Telemetry (Node 1)
  unsigned long now = millis();
  if (now - lastHeartbeat >= 1000) {
    lastHeartbeat = now;
    int stationCount = WiFi.softAPgetStationNum();

    // Generate Master Node status frame (Node ID: 1)
    // Modeled as a telemetry JSON object
    Serial.printf("{\"node_id\":1,\"role\":\"MASTER\",\"timestamp\":%lu,\"stations_connected\":%d,\"packets_relayed\":%lu,\"channel\":6,\"status\":\"ONLINE\"}\n",
                  now, stationCount, totalPacketsAggregated);
  }

  yield();
}
