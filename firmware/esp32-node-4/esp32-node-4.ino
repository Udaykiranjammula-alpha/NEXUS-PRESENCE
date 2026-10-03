/*
 * ============================================================
 * NEXUS-PRESENCE: ESP32 #4 - SENSOR NODE C (NODE_ID: 4)
 * Project: Multi-Node Ambient Wi-Fi Human Presence System
 * Author: Uday Kiran Jammula
 * 
 * Hardware: ESP32 DevKit v1 / ESP32-WROOM-32
 * Role: Ambient RF Sensor Station C (RSSI & CSI with auto-fallback)
 * ============================================================
 */

#include <WiFi.h>
#include <WiFiUdp.h>
#include "../common/csi/csi_collector.h"

#define NODE_ID 4
#define NODE_LABEL "SENSOR_NODE_C"
const char* AP_SSID = "NEXUS_PRESENCE";
const char* AP_PASS = "nexus123";
const IPAddress MASTER_IP(192, 168, 4, 1);
const uint16_t MASTER_PORT = 5005;

const int WINDOW_SIZE = 10;
const int CALIBRATION_SAMPLES = 20;
const int SAMPLE_INTERVAL_MS = 100;

WiFiUDP udp;
int rssiBuffer[WINDOW_SIZE];
int bufferIndex = 0;
float baseline = 0.0f;
float baselineVariance = 0.0f;
bool baselineReady = false;
uint32_t packetSequence = 0;
bool csiAvailable = false;

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("==================================================");
  Serial.printf("        NEXUS-PRESENCE: SENSOR NODE (ID: %d)       \n", NODE_ID);
  Serial.println("       Ambient Wi-Fi RF Sensing & Analysis        ");
  Serial.println("            Author: Uday Kiran Jammula            ");
  Serial.println("==================================================");

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);

  Serial.printf("[WIFI] Connecting to Master AP: %s", AP_SSID);
  WiFi.begin(AP_SSID, AP_PASS);

  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 40) {
    delay(500);
    Serial.print(".");
    retries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WIFI] Connected to Master AP!");
    Serial.print("[WIFI] Station IP: "); Serial.println(WiFi.localIP());
    Serial.print("[WIFI] Gateway IP: "); Serial.println(WiFi.gatewayIP());
    Serial.print("[WIFI] Initial RSSI: "); Serial.print(WiFi.RSSI()); Serial.println(" dBm");
  } else {
    Serial.println("\n[WIFI] ERROR: Connection failed. Check Master AP status.");
  }

  csiAvailable = csiCollector.init();
  if (csiAvailable) {
    Serial.println("[MODE] SENSING MODE: CSI + RSSI (Active)");
  } else {
    Serial.println("[MODE] SENSING MODE: RSSI ONLY (Hardware Fallback Active)");
  }

  Serial.println("\n[CALIBRATION] Starting empty-room baseline measurement...");
  Serial.println("[CALIBRATION] Keep zone empty and static for 5-10 seconds.");

  long sum = 0;
  long sumSq = 0;
  for (int i = 0; i < CALIBRATION_SAMPLES; i++) {
    int r = WiFi.RSSI();
    sum += r;
    sumSq += (r * r);
    rssiBuffer[i % WINDOW_SIZE] = r;
    delay(200);
    Serial.print("#");
  }
  Serial.println();

  baseline = (float)sum / CALIBRATION_SAMPLES;
  baselineVariance = (float)(sumSq / CALIBRATION_SAMPLES) - (baseline * baseline);
  baselineReady = true;

  Serial.printf("[CALIBRATION] Complete. Baseline: %.2f dBm, Variance: %.2f\n", baseline, baselineVariance);
  Serial.println("[STATUS] Sensor Node operational. Streaming telemetry...\n");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WIFI] Disconnected! Reconnecting...");
    WiFi.disconnect();
    WiFi.begin(AP_SSID, AP_PASS);
    delay(1000);
    return;
  }

  int rawRssi = WiFi.RSSI();
  rssiBuffer[bufferIndex] = rawRssi;
  bufferIndex = (bufferIndex + 1) % WINDOW_SIZE;

  long sum = 0;
  long sumSq = 0;
  for (int i = 0; i < WINDOW_SIZE; i++) {
    sum += rssiBuffer[i];
    sumSq += (rssiBuffer[i] * rssiBuffer[i]);
  }
  float avgRssi = (float)sum / WINDOW_SIZE;
  float variance = (float)(sumSq / WINDOW_SIZE) - (avgRssi * avgRssi);
  float deviation = fabs(avgRssi - baseline);

  float motionScore = deviation / 10.0f;
  if (motionScore > 1.0f) motionScore = 1.0f;
  if (motionScore < 0.0f) motionScore = 0.0f;

  const char* status = "STABLE";
  if (deviation < 2.0f) {
    status = "STABLE";
  } else if (deviation < 4.0f) {
    status = "LOW ACTIVITY";
  } else if (deviation < 7.0f) {
    status = "MOVEMENT";
  } else {
    status = "HIGH ACTIVITY";
  }

  packetSequence++;
  unsigned long now = millis();

  char jsonBuffer[512];
  if (csiAvailable) {
    CSIPacketMetadata csi = csiCollector.getLatestPacket();
    snprintf(jsonBuffer, sizeof(jsonBuffer),
      "{\"node_id\":%d,\"role\":\"%s\",\"timestamp\":%lu,\"rssi\":%d,\"channel\":%d,\"packet_count\":%lu,\"motion_score\":%.2f,\"average_rssi\":%.1f,\"baseline\":%.1f,\"deviation\":%.1f,\"variance\":%.2f,\"status\":\"%s\",\"sensing_mode\":\"CSI_RSSI\",\"csi_subcarriers\":%d,\"csi_variance\":%.2f}",
      NODE_ID, NODE_LABEL, now, rawRssi, WiFi.channel(), packetSequence, motionScore, avgRssi, baseline, deviation, variance, status, csi.subcarrier_count, csi.variance);
  } else {
    snprintf(jsonBuffer, sizeof(jsonBuffer),
      "{\"node_id\":%d,\"role\":\"%s\",\"timestamp\":%lu,\"rssi\":%d,\"channel\":%d,\"packet_count\":%lu,\"motion_score\":%.2f,\"average_rssi\":%.1f,\"baseline\":%.1f,\"deviation\":%.1f,\"variance\":%.2f,\"status\":\"%s\",\"sensing_mode\":\"RSSI_ONLY\"}",
      NODE_ID, NODE_LABEL, now, rawRssi, WiFi.channel(), packetSequence, motionScore, avgRssi, baseline, deviation, variance, status);
  }

  udp.beginPacket(MASTER_IP, MASTER_PORT);
  udp.write((const uint8_t*)jsonBuffer, strlen(jsonBuffer));
  udp.endPacket();

  Serial.println(jsonBuffer);
  delay(SAMPLE_INTERVAL_MS);
}
