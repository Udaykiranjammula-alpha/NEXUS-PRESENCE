# ESP32 Hardware Compatibility Matrix & CSI Feasibility Guide

**NEXUS-PRESENCE** employs distributed radio-frequency (RF) telemetry. Because Espressif microcontrollers feature diverse internal MAC/PHY architectures and varying versions of the Wi-Fi subsystem, Channel State Information (CSI) availability varies across chip families.

This document serves as the authoritative hardware reference for deploying NEXUS-PRESENCE.

---

## 1. ESP32 Family Feature Matrix

| Chip Model | Architecture | Wi-Fi Standard | Promiscuous Mode | CSI Hardware Support | Recommended ESP-IDF / Core | Operational Status in NEXUS-PRESENCE |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ESP32 (Classic WROOM/WROVER)** | Dual-core Xtensa LX6 (240 MHz) | 802.11 b/g/n (2.4 GHz) | **Full Support** | **Supported** (HT20: 52 / HT40: 114 subcarriers) | ESP-IDF v4.4 - v5.1 / Arduino ESP32 v2.0.14+ | **Primary Verified Prototype Platform** |
| **ESP32-S3** | Dual-core Xtensa LX7 (240 MHz) + Vector SIMD | 802.11 b/g/n (2.4 GHz) | **Full Support** | **Supported** (High stability, rich metadata) | ESP-IDF v4.4 - v5.2 / Arduino ESP32 v2.0.14+ | **Recommended for Production CSI** |
| **ESP32-S2** | Single-core Xtensa LX7 (240 MHz) | 802.11 b/g/n (2.4 GHz) | **Supported** | **Supported** (Limited RAM for large subcarrier ring buffers) | ESP-IDF v4.3+ | Supported (RSSI mode prioritized) |
| **ESP32-C3** | Single-core RISC-V (160 MHz) | 802.11 b/g/n (2.4 GHz) | **Supported** | **Supported** (Reduced buffer size required) | ESP-IDF v4.3+ | Supported |
| **ESP32-C6** | Single-core RISC-V (160 MHz) | 802.11ax (Wi-Fi 6, 2.4 GHz) | **Supported** | **Experimental** (Altered frame structure under Wi-Fi 6 OFDMA) | ESP-IDF v5.1+ | In Development |
| **ESP8266** | Single-core Xtensa L106 (80/160 MHz) | 802.11 b/g/n | Limited | **UNSUPPORTED** (Hardware PHY cannot export CSI) | Any | **Incompatible (RSSI-only legacy)** |

---

## 2. Hardware Fallback Policy

NEXUS-PRESENCE is architected to guarantee zero system downtime regardless of hardware model:

```
                  ┌──────────────────────────────────┐
                  │ ESP32 Node Boot / Firmware Probe  │
                  └─────────────────┬────────────────┘
                                    │
                    Has Hardware CSI Capability?
                                    │
                     ┌──────────────┴──────────────┐
                    YES                            NO
                     │                             │
         ┌───────────▼───────────┐     ┌───────────▼───────────┐
         │ Enable CSI Callback   │     │ Disable CSI Subsystem │
         │ Stream RSSI + CSI     │     │ Fallback to Pure RSSI │
         │ Mode: "CSI + RSSI"    │     │ Mode: "RSSI ONLY"     │
         └───────────────────────┘     └───────────────────────┘
```

1. **RSSI Mode (`RSSI_ONLY`)**:
   - Every ESP32 module universally measures Received Signal Strength Indication (RSSI) in standard Station and Promiscuous modes.
   - When CSI is unavailable, the system transparently executes the sliding-window deviation, variance filtering, and multilateration pipeline using RSSI measurements.
   - The UI displays: `SENSING MODE: RSSI ONLY`.

2. **CSI + RSSI Mode (`CSI_RSSI`)**:
   - Enabled when target chips support `esp_wifi_set_csi_rx_cb` and sufficient FreeRTOS heap memory is available.
   - Captures subcarrier amplitude and phase variation for finer spatial resolution.
   - The UI displays: `SENSING MODE: CSI + RSSI`.

---

## 3. Physical Node Deployment Recommendations

To minimize multipath distortion and maximize detection sensitivity:

1. **Anchor Geometry**: Mount 4 nodes at approximately human chest/torso height ($1.0\text{ m} - 1.5\text{ m}$ off the floor) along the four corners or opposing walls of the room.
2. **Line of Sight (LoS)**: Maintain direct line-of-sight paths between the Master AP (#1) and sensor stations (#2, #3, #4) across the primary room transit zone.
3. **Power Stability**: Use clean 5V/1A USB power supplies. Unfiltered or sagging power supplies cause RF front-end gain fluctuations that register as false motion artifacts.
4. **Channel Selection**: Configure the Master AP to a fixed, quiet 2.4 GHz Wi-Fi channel (Channel 1, 6, or 11) with low external co-channel interference.

---

## 4. Current Hardware Configuration Placeholder

If you are connecting a new or unverified ESP32 module, execute the hardware probe script:
```bash
python scripts/detect_esp32.py --port COM3
```
This inspects the chip family via `esptool.py` (or serial bootloader ROM info) and prints the recommended configuration flags.
