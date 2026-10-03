#include "csi_collector.h"
#include <math.h>

CSICollector csiCollector;

CSICollector::CSICollector() 
    : _is_supported(false), 
      _is_enabled(false), 
      _total_packets(0), 
      _csi_mux(portMUX_INITIALIZER_UNLOCKED) {
    memset(&_latest_packet, 0, sizeof(CSIPacketMetadata));
}

CSICollector::~CSICollector() {
    stop();
}

bool CSICollector::isHardwareSupported() const {
#if defined(ESP32) && !defined(CONFIG_IDF_TARGET_ESP8266)
    return true;
#else
    return false;
#endif
}

bool CSICollector::isEnabled() const {
    return _is_enabled;
}

void CSICollector::handleIncomingCSI(void *ctx, wifi_csi_info_t *data) {
    if (!ctx || !data || !data->buf) return;
    
    CSICollector *collector = static_cast<CSICollector*>(ctx);
    wifi_pkt_rx_ctrl_t rx_ctrl = data->rx_ctrl;
    
    taskENTER_CRITICAL_ISR(&(collector->_csi_mux));

    collector->_latest_packet.timestamp_ms = millis();
    collector->_latest_packet.rssi = rx_ctrl.rssi;
    collector->_latest_packet.channel = rx_ctrl.channel;
    collector->_total_packets++;
    collector->_latest_packet.packet_count = collector->_total_packets;

    // Subcarriers parsing (Classic HT20 provides signed byte pairs of imaginary and real components)
    int len = data->len;
    int subcarriers = len / 2;
    if (subcarriers > CSI_MAX_SUBCARRIERS) subcarriers = CSI_MAX_SUBCARRIERS;

    collector->_latest_packet.subcarrier_count = subcarriers;

    int8_t *csi_buf = (int8_t*)data->buf;
    double sum_amp = 0.0;
    double sum_sq_amp = 0.0;

    for (int i = 0; i < subcarriers; i++) {
        int8_t imag = csi_buf[i * 2];
        int8_t real = csi_buf[i * 2 + 1];

        // Amplitude = sqrt(real^2 + imag^2)
        float amp = sqrtf((float)(real * real + imag * imag));
        if (amp > 255.0f) amp = 255.0f;
        collector->_latest_packet.amplitudes[i] = (uint8_t)amp;

        // Phase = atan2(imag, real) converted to -128..127 range
        float phase = atan2f((float)imag, (float)real);
        collector->_latest_packet.phases[i] = (int8_t)(phase * (127.0f / 3.14159265f));

        sum_amp += amp;
        sum_sq_amp += (amp * amp);
    }

    if (subcarriers > 0) {
        double mean = sum_amp / subcarriers;
        collector->_latest_packet.variance = (float)((sum_sq_amp / subcarriers) - (mean * mean));
    } else {
        collector->_latest_packet.variance = 0.0f;
    }

    collector->_latest_packet.is_valid = true;

    taskEXIT_CRITICAL_ISR(&(collector->_csi_mux));
}

bool CSICollector::init() {
#if defined(ESP32)
    Serial.println("[CSI] Probing ESP32 CSI capability...");
    
    wifi_csi_config_t csi_config = {
        .lltf_en = 1,
        .htltf_en = 1,
        .stbc_htltf2_en = 1,
        .ltf_merge_en = 1,
        .channel_filter_en = 1,
        .manu_scale = 0
    };

    esp_err_t err = esp_wifi_set_csi_config(&csi_config);
    if (err != ESP_OK) {
        Serial.printf("[CSI] Failed to configure CSI (err: 0x%x). Fallback to RSSI_ONLY.\n", err);
        _is_supported = false;
        _is_enabled = false;
        return false;
    }

    err = esp_wifi_set_csi_rx_cb(&CSICollector::handleIncomingCSI, this);
    if (err != ESP_OK) {
        Serial.printf("[CSI] Failed to register CSI callback (err: 0x%x). Fallback to RSSI_ONLY.\n", err);
        _is_supported = false;
        _is_enabled = false;
        return false;
    }

    err = esp_wifi_set_csi(true);
    if (err != ESP_OK) {
        Serial.printf("[CSI] Failed to enable CSI mode (err: 0x%x). Fallback to RSSI_ONLY.\n", err);
        _is_supported = false;
        _is_enabled = false;
        return false;
    }

    _is_supported = true;
    _is_enabled = true;
    Serial.println("[CSI] Hardware CSI callback initialized successfully. Mode: CSI_RSSI");
    return true;
#else
    Serial.println("[CSI] Hardware does not support ESP-IDF CSI. Running in RSSI_ONLY mode.");
    _is_supported = false;
    _is_enabled = false;
    return false;
#endif
}

void CSICollector::stop() {
#if defined(ESP32)
    if (_is_enabled) {
        esp_wifi_set_csi(false);
        esp_wifi_set_csi_rx_cb(NULL, NULL);
        _is_enabled = false;
    }
#endif
}

CSIPacketMetadata CSICollector::getLatestPacket() {
    CSIPacketMetadata packet;
    taskENTER_CRITICAL(&_csi_mux);
    packet = _latest_packet;
    taskEXIT_CRITICAL(&_csi_mux);
    return packet;
}

uint32_t CSICollector::getTotalCaptured() const {
    return _total_packets;
}

float CSICollector::getSubcarrierVariance() const {
    return _latest_packet.variance;
}
