# Contributing to NEXUS-PRESENCE

Thank you for your interest in contributing to **NEXUS-PRESENCE: Multi-Node Ambient Wi-Fi Human Presence, Movement & 3D Visualization System**!

This project bridges embedded firmware (ESP-IDF/Arduino), RF signal processing, mathematical localization, and real-time Three.js graphics. We welcome contributions that improve algorithmic accuracy, firmware stability, documentation clarity, and cross-platform compatibility.

---

## 1. Code of Conduct & Scientific Honesty

- **Honesty in RF Sensing**: We strictly maintain realistic, technically verifiable claims. Never claim that RSSI or single-antenna CSI provides optical camera resolution, through-wall X-ray vision, or anatomical skeleton imaging.
- **Hardware Transparency**: Distinguish clearly between features verified on physical hardware vs. synthetic or simulated models.
- **Privacy & Ethics**: This project is designed for ambient non-invasive presence detection (e.g., elderly fall alerting, occupancy counting) without intrusive optical cameras. Respect user privacy in all contributions.

---

## 2. Development Workflow

### Branch Naming Convention
Use descriptive prefixes for branches:
- `feat/feature-name` - New features or capabilities
- `fix/bug-fix` - Bug fixes or corrections
- `firmware/esp32-enhancement` - Firmware specific modifications
- `docs/documentation-update` - Updates to technical documentation or diagrams
- `test/test-addition` - New unit or simulation tests

### Commit Message Guidelines
We follow standard Conventional Commits:
```text
<type>(<scope>): <short description>

[optional detailed body]
```
Examples:
- `feat(processing): add butterworth bandpass filter for csi subcarriers`
- `fix(firmware): resolve memory leak in circular rssi buffer`
- `docs(hardware): document esp32-s3 promiscuous csi support limitations`

---

## 3. Pull Request Process

1. Fork the repository and create your branch from `main`.
2. Ensure all unit tests pass locally:
   ```bash
   pytest tests/
   ```
3. Run Python linting and formatting:
   ```bash
   ruff check .  # or flake8
   ```
4. If modifying firmware, test build using Arduino IDE or PlatformIO:
   ```bash
   pio run
   ```
5. Update relevant documentation in `docs/` or `README.md` if your change affects configuration or hardware requirements.
6. Open a Pull Request with a clear summary of changes, motivation, and physical/simulated testing evidence.

---

## 4. Hardware Verification Guidelines

When submitting firmware or signal processing PRs:
- State the exact microcontroller model tested (e.g., `ESP32-WROOM-32D`, `ESP32-S3-WROOM-1`).
- Include baud rate, COM port configuration, and sample Serial Monitor output.
- If hardware was not available, explicitly state: **"Simulated with demo_server.py / synthetic telemetry"**.

---

## 5. Contact & Questions

For architecture discussions, reach out to the project maintainer:
- **Lead Developer**: Uday Kiran Jammula
- **Repository**: [https://github.com/Udaykiranjammula-alpha/NEXUS-PRESENCE](https://github.com/Udaykiranjammula-alpha/NEXUS-PRESENCE)
