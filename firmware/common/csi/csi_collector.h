#ifndef NEXUS_CSI_COLLECTOR_H
#define NEXUS_CSI_COLLECTOR_H

#include <Arduino.h>
#include <WiFi.h>

#if defined(ESP32)
#include "esp_wifi.h"
#include "esp_err.h"
#endif

#define CSI_MAX_SUBCARRIERS 64

struct CSIPacketMetadata {
    uint32_t timestamp_ms;
    int8_t rssi;
    uint8_t channel;
    uint32_t packet_count;
    uint8_t subcarrier_count;
    uint8_t amplitudes[CSI_MAX_SUBCARRIERS];
    int8_t phases[CSI_MAX_SUBCARRIERS];
    float variance;
    bool is_valid;
};

class CSICollector {
public:
    CSICollector();
    ~CSICollector();

    bool init();
    void stop();
    bool isHardwareSupported() const;
    bool isEnabled() const;
    
    CSIPacketMetadata getLatestPacket();
    uint32_t getTotalCaptured() const;
    float getSubcarrierVariance() const;

    static void handleIncomingCSI(void *ctx, wifi_csi_info_t *data);

private:
    bool _is_supported;
    bool _is_enabled;
    uint32_t _total_packets;
    CSIPacketMetadata _latest_packet;
    portMUX_TYPE _csi_mux;
};

extern CSICollector csiCollector;

#endif // NEXUS_CSI_COLLECTOR_H
