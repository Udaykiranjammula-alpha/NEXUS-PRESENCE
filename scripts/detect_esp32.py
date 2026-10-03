"""
Hardware Compatibility Probe & ESP32 Chip Identification Utility
Author: Uday Kiran Jammula
"""

import sys
try:
    import serial.tools.list_ports
    HAS_PYSERIAL = True
except ImportError:
    HAS_PYSERIAL = False

import argparse

def scan_serial_ports():
    print("==================================================")
    print("   NEXUS-PRESENCE: ESP32 HARDWARE PROBE TOOL      ")
    print("==================================================")
    if not HAS_PYSERIAL:
        print("[!] Note: 'pyserial' is not installed. To scan COM ports automatically:")
        print("    Run: pip install pyserial")
        print("    Skipping live port enumeration...")
        return []

    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("[!] No active COM / Serial ports detected.")
        print("    Please connect your ESP32 board via micro-USB / USB-C.")
        return []

    print(f"Found {len(ports)} connected serial port(s):")
    for p in ports:
        print(f"  -> Port: {p.device:<10} | Description: {p.description} | HWID: {p.hwid}")
    return ports

def analyze_hardware(chip_name: str = "ESP32-WROOM-32"):
    print("\n--- HARDWARE CAPABILITY ASSESSMENT ---")
    chip_upper = chip_name.upper()
    print(f"Target Chip: {chip_upper}")

    if "S3" in chip_upper:
        print(" [OK] Promiscuous Mode: Supported")
        print(" [OK] CSI Hardware: Full Support (High Fidelity Subcarriers)")
        print(" [OK] Recommended Firmware Mode: CSI_RSSI")
        print(" [OK] Recommended Framework: ESP-IDF v5.1+ / Arduino ESP32 v2.0.14+")
    elif "C3" in chip_upper:
        print(" [OK] Promiscuous Mode: Supported")
        print(" [OK] CSI Hardware: Supported (Single-core RISC-V)")
        print(" [OK] Recommended Firmware Mode: CSI_RSSI or RSSI_ONLY")
    elif "S2" in chip_upper:
        print(" [OK] Promiscuous Mode: Supported")
        print(" [~]  CSI Hardware: Limited RAM (buffer tuning required)")
        print(" [OK] Recommended Firmware Mode: RSSI_ONLY (fallback)")
    elif "ESP32" in chip_upper or "WROOM" in chip_upper or "WROVER" in chip_upper:
        print(" [OK] Promiscuous Mode: Full Support")
        print(" [OK] CSI Hardware: Supported via ESP-IDF APIs")
        print(" [OK] Status: Verified Working Prototype Platform")
        print(" [OK] Recommended Firmware Mode: CSI_RSSI (with auto-fallback to RSSI_ONLY)")
    else:
        print(" [!]  Unknown hardware variant. Defaulting to RSSI_ONLY fallback mode.")

def main():
    parser = argparse.ArgumentParser(description="Probe ESP32 hardware capability for NEXUS-PRESENCE")
    parser.add_argument("--chip", default="ESP32-WROOM-32", help="Chip model string (e.g. ESP32-WROOM-32, ESP32-S3)")
    args = parser.parse_args()

    scan_serial_ports()
    analyze_hardware(args.chip)

if __name__ == "__main__":
    main()
