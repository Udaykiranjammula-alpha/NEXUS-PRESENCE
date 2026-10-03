# Changelog

All notable changes to the **NEXUS-PRESENCE** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v0.1.0] - 2026-10-03 (VERIFIED PROTOTYPE)

### Added
- **ESP32 Master AP Node (#1)**: Working softAP mode (`SSID: NEXUS_PRESENCE`, `IP: 192.168.4.1`, station counter). Verified hardware prototype.
- **ESP32 Sensor Station Node (#2)**: Working station connection to Master AP, raw RSSI sampling loop at 250ms interval. Verified hardware prototype.
- **Sensor Baseline & Activity Detector (v2)**: Sliding circular window (`WINDOW_SIZE=10`), 10-second empty-room baseline calibration, deviation computation, and discrete state classification (`STABLE`, `LOW ACTIVITY`, `MOVEMENT`, `HIGH ACTIVITY`). Verified hardware prototype.
- **Core Signal Protocol**: Standardized JSON telemetry format definition for multi-node wireless transmission.
- **Hardware Compatibility Matrix**: Documentation covering ESP32 variants (WROOM-32, S2, S3, C3, C6), promiscuous mode, and CSI support limits.

---

## [v0.2.0] - 2026-10-03 (IMPLEMENTED - CSI & SIGNAL PIPELINE)

### Added
- **Modular CSI Capture Layer**: ESP-IDF / Arduino compatible CSI callback hook with hardware capability check and automatic fallback.
- **Python Processing Engine**:
  - `rssi_processor.py`: Moving average, variance calculation, and adaptive baseline tracking.
  - `csi_processor.py`: Subcarrier amplitude extraction, high-frequency subcarrier variance, phase difference sanitization.
  - `noise_filter.py`: Exponential smoothing (EMA), Median filtering, and Outlier rejection.
  - `feature_extraction.py`: Statistical moments, energy spectral density, and differential features.
  - `motion_detector.py`: Multi-threshold heuristic and energy-based motion scoring.
  - `signal_fusion.py`: Multi-node spatial weight fusion combining confidence-weighted node deviations.

---

## [v0.3.0] - 2026-10-03 (IMPLEMENTED - FOUR-NODE ARCHITECTURE)

### Added
- **ESP32 Node #3 & Node #4 Firmware**: Dedicated sensor node implementations with unique identifiers, configurable target APs, and UDP/Serial streaming.
- **Master Telemetry Aggregator**: Firmware logic for ESP32 #1 to collect packets from Nodes #2, #3, and #4 and relay structured telemetry over Serial/WebSocket.
- **UDP Receiver Service**: Async Python background listener for low-latency multi-node UDP broadcast packets.

---

## [v0.4.0] - 2026-10-03 (IMPLEMENTED - LOCALIZATION ENGINE)

### Added
- **Coordinate System**: Configurable 3D Cartesian space with bounding box checks and anchor placement.
- **Trilateration Engine**: Log-distance path loss (LDPL) range estimation combined with non-linear least-squares spatial optimization.
- **Position Estimator**: Extended Kalman / Exponential smoothing position filter with velocity and direction calculation.
- **Confidence Scoring**: Dynamic confidence metric factoring geometric dilution of precision (GDOP), signal variance, and node health.

---

## [v0.5.0] - 2026-10-03 (IMPLEMENTED - 3D VISUALIZATION & DASHBOARD)

### Added
- **Three.js Virtual Environment**:
  - Procedural 3D room with floor grid, translucent boundary walls, studio lighting, and OrbitControls.
  - 3D physical sensor node models with active RF pulse animations and color-coded telemetry status rings.
  - Dynamic RF signal rays connecting nodes to the estimated target coordinates.
  - Procedural humanoid avatar with articulated head, torso, arms, legs, and walking kinematics.
  - Dead-reckoning and smooth position interpolation (slerp/lerp).
- **Mission Control Web Dashboard**:
  - Real-time node status cards (Master, Node 2, Node 3, Node 4).
  - Person tracking metrics HUD (X, Y, Z, Velocity, Heading, State, Confidence).
  - High-frequency live canvas signal charts (RSSI & Motion Score).
- **Dual Sensing Mode Indicator**: Automatic toggle and HUD display between `CSI + RSSI` and `RSSI ONLY`.

---

## [v1.0.0] - 2026-10-03 (INTEGRATED SYSTEM RELEASE)

### Added
- **Full System Integration**: Seamless end-to-end telemetry pipeline from ESP32 nodes -> UDP -> FastAPI backend -> WebSocket -> Three.js frontend.
- **Demo Mode**: Built-in synthetic walk simulation engine (`demo_server.py`) with trajectory generation, noise modeling, and distinct `SIMULATION MODE` HUD badge.
- **Automated Test Suite**: Executable unit tests for RSSI processing, CSI handling, motion classification, and localization triangulation.
- **Deployment Artifacts**: Dockerfile, docker-compose.yml, and Nginx production config.
- **Documentation Suite**: High-resolution architecture diagrams, comprehensive README, hardware reference, and research notes.
