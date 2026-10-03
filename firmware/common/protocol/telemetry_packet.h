#ifndef NEXUS_TELEMETRY_PACKET_H
#define NEXUS_TELEMETRY_PACKET_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define NEXUS_PROTOCOL_VERSION 1
#define NEXUS_MAX_CSI_SUBCARRIERS 64
#define NEXUS_UDP_PORT 5005

typedef enum {
    NEXUS_STATUS_STABLE = 0,
    NEXUS_STATUS_LOW_ACTIVITY = 1,
    NEXUS_STATUS_MOVEMENT = 2,
    NEXUS_STATUS_HIGH_ACTIVITY = 3
} nexus_motion_status_t;

typedef enum {
    NEXUS_MODE_RSSI_ONLY = 0,
    NEXUS_MODE_CSI_RSSI = 1
} nexus_sensing_mode_t;

typedef struct __attribute__((packed)) {
    uint8_t protocol_version;
    uint8_t node_id;               // 1: Master, 2: Node A, 3: Node B, 4: Node C
    uint8_t sensing_mode;          // 0: RSSI only, 1: CSI + RSSI
    uint8_t channel;               // Wi-Fi channel (1-13)
    int8_t  rssi;                  // Signal strength in dBm (-100 to 0)
    uint8_t status;                // nexus_motion_status_t
    uint32_t timestamp_ms;         // Node uptime or Unix epoch millis
    uint32_t packet_count;         // Monotonic packet sequence counter
    float   motion_score;          // Normalized 0.0 - 1.0 motion index
    float   average_rssi;          // Smoothed window average RSSI
    float   baseline_rssi;         // Calibrated baseline RSSI
    float   deviation;             // Absolute difference from baseline
    uint8_t csi_subcarrier_count;  // Count of subcarrier amplitudes attached (0 if RSSI only)
    uint8_t csi_amplitudes[NEXUS_MAX_CSI_SUBCARRIERS]; // Raw subcarrier amplitudes
} nexus_telemetry_packet_t;

static inline const char* nexus_status_to_string(nexus_motion_status_t status) {
    switch (status) {
        case NEXUS_STATUS_STABLE: return "STABLE";
        case NEXUS_STATUS_LOW_ACTIVITY: return "LOW ACTIVITY";
        case NEXUS_STATUS_MOVEMENT: return "MOVEMENT";
        case NEXUS_STATUS_HIGH_ACTIVITY: return "HIGH ACTIVITY";
        default: return "UNKNOWN";
    }
}

#ifdef __cplusplus
}
#endif

#endif // NEXUS_TELEMETRY_PACKET_H
