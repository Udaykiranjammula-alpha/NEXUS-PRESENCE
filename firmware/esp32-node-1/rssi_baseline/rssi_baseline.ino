/*
 * ============================================================
 * NEXUS-PRESENCE: SENSOR NODE (VERIFIED PROTOTYPE v2)
 * Role: Sliding Window RSSI Baseline & Activity Classifier
 * Hardware: ESP32 DevKit v1 / ESP32-WROOM-32
 * Developed by: Uday Kiran Jammula
 * Status: TESTED & VERIFIED WORKING PROTOTYPE
 * ============================================================
 */

#include <WiFi.h>

const char* ssid = "NEXUS_PRESENCE";
const char* password = "nexus123";

const int WINDOW_SIZE = 10;

int rssiBuffer[WINDOW_SIZE];
int bufferIndex = 0;

float baseline = 0;
bool baselineReady = false;

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("======================================");
  Serial.println("       NEXUS-PRESENCE v2");
  Serial.println("          SENSOR NODE");
  Serial.println("======================================");

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  Serial.print("Connecting");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("CONNECTED!");

  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  Serial.println();
  Serial.println("Calibrating baseline...");
  Serial.println("Keep the area empty for 10 seconds.");
  Serial.println();

  for (int i = 0; i < WINDOW_SIZE; i++) {
    rssiBuffer[i] = WiFi.RSSI();
    delay(100);
  }

  long total = 0;
  for (int i = 0; i < WINDOW_SIZE; i++) {
    total += rssiBuffer[i];
  }

  baseline = (float)total / WINDOW_SIZE;
  baselineReady = true;

  Serial.print("Baseline RSSI: ");
  Serial.print(baseline);
  Serial.println(" dBm");

  Serial.println();
  Serial.println("SYSTEM READY");
  Serial.println("--------------------------------------");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi connection lost!");
    WiFi.disconnect();
    WiFi.begin(ssid, password);
    delay(1000);
    return;
  }

  int rssi = WiFi.RSSI();

  rssiBuffer[bufferIndex] = rssi;
  bufferIndex++;

  if (bufferIndex >= WINDOW_SIZE) {
    bufferIndex = 0;
  }

  long total = 0;

  for (int i = 0; i < WINDOW_SIZE; i++) {
    total += rssiBuffer[i];
  }

  float averageRSSI = (float)total / WINDOW_SIZE;
  float deviation = abs(averageRSSI - baseline);

  String status;

  if (deviation < 2.0) {
    status = "STABLE";
  }
  else if (deviation < 4.0) {
    status = "LOW ACTIVITY";
  }
  else if (deviation < 7.0) {
    status = "MOVEMENT";
  }
  else {
    status = "HIGH ACTIVITY";
  }

  Serial.print("RSSI=");
  Serial.print(rssi);
  Serial.print(" | AVG=");
  Serial.print(averageRSSI, 1);
  Serial.print(" | BASE=");
  Serial.print(baseline, 1);
  Serial.print(" | DEV=");
  Serial.print(deviation, 1);
  Serial.print(" | STATUS=");
  Serial.println(status);

  delay(250);
}
