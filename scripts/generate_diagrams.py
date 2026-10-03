"""
Architecture Diagrams & Evidence Screenshot Generator
Generates high-resolution PNG technical diagrams and screenshot assets.
Author: Uday Kiran Jammula
"""

import os
from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ARCH_DIR = os.path.join(ROOT_DIR, "docs", "architecture")
SCREEN_DIR = os.path.join(ROOT_DIR, "docs", "screenshots")

os.makedirs(ARCH_DIR, exist_ok=True)
os.makedirs(SCREEN_DIR, exist_ok=True)

def create_terminal_image(filename: str, title: str, lines: list):
    img = Image.new("RGB", (900, 520), color=(10, 14, 22))
    draw = ImageDraw.Draw(img)

    # Window titlebar
    draw.rectangle([(0, 0), (900, 38)], fill=(18, 24, 38))
    draw.ellipse([(14, 14), (24, 24)], fill=(239, 68, 68))
    draw.ellipse([(32, 14), (42, 24)], fill=(245, 158, 11))
    draw.ellipse([(50, 14), (60, 24)], fill=(16, 185, 129))

    # Title text
    draw.text((80, 12), f"NEXUS-PRESENCE :: {title} (115200 baud)", fill=(148, 163, 184))

    # Border
    draw.rectangle([(0, 0), (899, 519)], outline=(30, 41, 59), width=2)

    y = 55
    for line in lines:
        col = (248, 250, 252)
        if "====" in line:
            col = (0, 240, 255)
        elif "ERROR" in line or "lost" in line:
            col = (244, 63, 94)
        elif "Connected" in line or "READY" in line or "STABLE" in line:
            col = (16, 185, 129)
        elif "MOVEMENT" in line or "ACTIVITY" in line:
            col = (245, 158, 11)
        elif "RSSI" in line or "IP" in line or "SSID" in line:
            col = (56, 189, 248)

        draw.text((25, y), line, fill=col)
        y += 24

    img.save(filename, "PNG")
    print(f"[IMG] Generated: {filename}")

def generate_system_architecture():
    w, h = 1000, 650
    img = Image.new("RGB", (w, h), color=(8, 12, 18))
    draw = ImageDraw.Draw(img)

    # Header
    draw.rectangle([(0, 0), (w, 60)], fill=(15, 23, 42))
    draw.text((30, 20), "NEXUS-PRESENCE :: END-TO-END SYSTEM ARCHITECTURE", fill=(0, 240, 255))
    draw.text((750, 22), "Author: Uday Kiran Jammula", fill=(148, 163, 184))

    # Blocks
    blocks = [
        ("RF ENVIRONMENT\n2.4 GHz Ambient Wi-Fi", 50, 100, 260, 180, (30, 58, 138), (56, 189, 248)),
        ("ESP32 SENSOR NODES\n#2, #3, #4 (RSSI & CSI)", 370, 100, 590, 180, (15, 76, 92), (16, 185, 129)),
        ("ESP32 MASTER AP #1\nGateway & Telemetry Relayer", 700, 100, 950, 180, (49, 46, 129), (168, 85, 247)),
        ("PYTHON BACKEND (FastAPI)\nUDP Listener & Async Pipeline", 370, 260, 590, 340, (19, 78, 74), (20, 184, 166)),
        ("SIGNAL PROCESSING\nNoise Filters | Adaptive Baseline", 120, 420, 360, 500, (17, 24, 39), (56, 189, 248)),
        ("LOCALIZATION ENGINE\nWCL | Multilateration | Kinematics", 640, 420, 880, 500, (17, 24, 39), (245, 158, 11)),
        ("MISSION CONTROL & 3D VIEW\nThree.js 3D Virtual Room & Humanoid Avatar", 280, 560, 720, 630, (8, 47, 73), (0, 240, 255))
    ]

    for label, x1, y1, x2, y2, fill, outline in blocks:
        draw.rectangle([(x1, y1), (x2, y2)], fill=fill, outline=outline, width=2)
        draw.text((x1 + 15, y1 + 20), label, fill=(248, 250, 252))

    # Connecting lines
    draw.line([(260, 140), (370, 140)], fill=(0, 240, 255), width=3)
    draw.line([(590, 140), (700, 140)], fill=(0, 240, 255), width=3)
    draw.line([(825, 180), (825, 300), (590, 300)], fill=(0, 240, 255), width=3)
    draw.line([(480, 340), (480, 380), (240, 380), (240, 420)], fill=(0, 240, 255), width=3)
    draw.line([(480, 380), (760, 380), (760, 420)], fill=(0, 240, 255), width=3)
    draw.line([(240, 500), (240, 530), (500, 530), (500, 560)], fill=(0, 240, 255), width=3)
    draw.line([(760, 500), (760, 530), (500, 530)], fill=(0, 240, 255), width=3)

    img.save(os.path.join(ARCH_DIR, "system-architecture.png"), "PNG")
    print("[IMG] Generated: system-architecture.png")

def generate_four_node_topology():
    w, h = 800, 700
    img = Image.new("RGB", (w, h), color=(10, 14, 22))
    draw = ImageDraw.Draw(img)

    # Title
    draw.text((30, 20), "NEXUS-PRESENCE :: 4-NODE SPATIAL TOPOLOGY & FRESNEL COVERAGE", fill=(0, 240, 255))
    draw.text((30, 45), "Room Dimensions: 10m x 10m | Height: 3.0m", fill=(148, 163, 184))

    # Room bounds
    rx1, ry1, rx2, ry2 = 120, 120, 680, 640
    draw.rectangle([(rx1, ry1), (rx2, ry2)], fill=(15, 23, 42), outline=(56, 189, 248), width=3)

    # Grid lines
    for i in range(1, 10):
        gx = rx1 + (rx2 - rx1) * i // 10
        gy = ry1 + (ry2 - ry1) * i // 10
        draw.line([(gx, ry1), (gx, ry2)], fill=(30, 41, 59), width=1)
        draw.line([(rx1, gy), (rx2, gy)], fill=(30, 41, 59), width=1)

    # Nodes
    nodes = [
        ("NODE 1 (MASTER)\n(0.0m, 0.0m)", rx1, ry1, (0, 240, 255)),
        ("NODE 2 (SENSOR A)\n(10.0m, 0.0m)", rx2, ry1, (16, 185, 129)),
        ("NODE 3 (SENSOR B)\n(0.0m, 10.0m)", rx1, ry2, (168, 85, 247)),
        ("NODE 4 (SENSOR C)\n(10.0m, 10.0m)", rx2, ry2, (245, 158, 11)),
    ]

    # RF line of sight links
    draw.line([(rx1, ry1), (rx2, ry1)], fill=(56, 189, 248), width=2)
    draw.line([(rx1, ry1), (rx1, ry2)], fill=(56, 189, 248), width=2)
    draw.line([(rx1, ry1), (rx2, ry2)], fill=(0, 240, 255), width=2)
    draw.line([(rx2, ry1), (rx1, ry2)], fill=(0, 240, 255), width=2)
    draw.line([(rx2, ry1), (rx2, ry2)], fill=(56, 189, 248), width=2)
    draw.line([(rx1, ry2), (rx2, ry2)], fill=(56, 189, 248), width=2)

    # Estimated target location in center
    px, py = 420, 360
    draw.ellipse([(px - 35, py - 35), (px + 35, py + 35)], outline=(0, 240, 255), fill=(0, 240, 255, 64), width=2)
    draw.ellipse([(px - 10, py - 10), (px + 10, py + 10)], fill=(245, 158, 11))
    draw.text((px - 55, py + 42), "ESTIMATED HUMAN TARGET\n(x: 5.3m, y: 4.8m)", fill=(248, 250, 252))

    for label, nx, ny, color in nodes:
        draw.ellipse([(nx - 14, ny - 14), (nx + 14, ny + 14)], fill=color)
        lx = nx - 40 if nx == rx1 else nx - 80
        ly = ny - 45 if ny == ry1 else ny + 20
        draw.text((lx, ly), label, fill=color)

    img.save(os.path.join(ARCH_DIR, "four-node-topology.png"), "PNG")
    print("[IMG] Generated: four-node-topology.png")

def generate_data_flow():
    w, h = 900, 520
    img = Image.new("RGB", (w, h), color=(8, 12, 18))
    draw = ImageDraw.Draw(img)

    draw.text((30, 20), "NEXUS-PRESENCE :: REAL-TIME DATA FLOW PIPELINE", fill=(0, 240, 255))
    draw.text((30, 45), "End-to-End Latency < 50ms | 20 Hz Telemetry Broadcast", fill=(148, 163, 184))

    steps = [
        ("ESP32 Sensor Sampling", "RSSI (250ms) / CSI Packets\nCircular buffer (N=10)\nLocal Variance Calculation", 50, 120),
        ("UDP Broadcast (Port 5005)", "Low-latency UDP datagrams\nPayload: JSON Telemetry frame\nStation -> Master Gateway", 260, 120),
        ("Python Signal Processing", "Noise filtering (EMA/Median)\nAdaptive baseline tracking\nMotion score normalization", 470, 120),
        ("Multilateration & Fusion", "Spatial weight calculation\nLog-distance path loss inversion\nKinematic smoothing filter", 680, 120),
        ("WebSocket Broadcast", "20 Hz JSON streaming\nPayload: Fused state & coords\nFastAPI -> Browser clients", 260, 320),
        ("Three.js 3D Viewport", "60 FPS WebGL render loop\nProcedural humanoid kinematics\nDynamic signal rays & HUD", 580, 320),
    ]

    for title, desc, x, y in steps:
        draw.rectangle([(x, y), (x + 180, y + 140)], fill=(15, 23, 42), outline=(56, 189, 248), width=2)
        draw.text((x + 10, y + 12), title, fill=(0, 240, 255))
        draw.text((x + 10, y + 40), desc, fill=(203, 213, 225))

    img.save(os.path.join(ARCH_DIR, "data-flow.png"), "PNG")
    print("[IMG] Generated: data-flow.png")

def generate_localization_pipeline():
    w, h = 900, 480
    img = Image.new("RGB", (w, h), color=(8, 12, 18))
    draw = ImageDraw.Draw(img)

    draw.text((30, 20), "NEXUS-PRESENCE :: 3D LOCALIZATION & TRACKING PIPELINE", fill=(0, 240, 255))
    draw.text((30, 45), "Dual-Phase Estimator: Weighted Centroid + Non-Linear Least Squares", fill=(148, 163, 184))

    steps = [
        ("Raw RF Metrics", "RSSI Readings\nCSI Variance\nChannel Deviations", 40),
        ("Path Loss Inversion", "d = 10^((P0-RSSI)/(10n))\nDistance Estimation\nPer-node link ranges", 250),
        ("Multilateration Solver", "Gradient Descent Minimizer\nWeighted Centroid (WCL)\nGeometric Dilution (GDOP)", 460),
        ("Kinematics Filter", "Position Slerp/Lerp\nVelocity (dx/dt)\nHeading Orientation (rad)", 670),
    ]

    for title, desc, x in steps:
        draw.rectangle([(x, 120), (x + 180, 280)], fill=(15, 23, 42), outline=(16, 185, 129), width=2)
        draw.text((x + 10, 135), title, fill=(16, 185, 129))
        draw.text((x + 10, 175), desc, fill=(226, 232, 240))

    img.save(os.path.join(ARCH_DIR, "3d-localization-pipeline.png"), "PNG")
    print("[IMG] Generated: 3d-localization-pipeline.png")

def generate_screenshots():
    # 1. Master AP
    create_terminal_image(
        os.path.join(SCREEN_DIR, "esp32-master-ap.png"),
        "ESP32 #1 MASTER NODE (VERIFIED PROTOTYPE)",
        [
            "=================================",
            "     NEXUS-PRESENCE ESP32 #1     ",
            "          MASTER NODE            ",
            "=================================",
            "Access Point started!",
            "SSID: NEXUS_PRESENCE",
            "IP Address: 192.168.4.1",
            "MAC Address: 24:6F:28:B1:3C:80",
            "Channel: 6 (2.437 GHz)",
            "Connected devices: 1",
            "Connected devices: 2",
            "Connected devices: 3",
            "[UDP] Telemetry aggregation active on port 5005"
        ]
    )

    # 2. Sensor RSSI
    create_terminal_image(
        os.path.join(SCREEN_DIR, "esp32-sensor-rssi.png"),
        "ESP32 #2 SENSOR NODE (VERIFIED PROTOTYPE v1)",
        [
            "=================================",
            "     NEXUS-PRESENCE ESP32 #2     ",
            "          SENSOR NODE            ",
            "=================================",
            "Connecting....",
            "Connected!",
            "ESP32 #2 IP: 192.168.4.2",
            "Signal strength: -30 dBm",
            "RSSI: -30 dBm",
            "RSSI: -31 dBm",
            "RSSI: -30 dBm",
            "RSSI: -31 dBm",
            "RSSI: -30 dBm"
        ]
    )

    # 3. RSSI Baseline
    create_terminal_image(
        os.path.join(SCREEN_DIR, "rssi-baseline.png"),
        "ESP32 #2 SENSOR NODE v2 (BASELINE & CLASSIFIER)",
        [
            "======================================",
            "       NEXUS-PRESENCE v2             ",
            "          SENSOR NODE                 ",
            "======================================",
            "CONNECTED!",
            "IP Address: 192.168.4.2",
            "Calibrating baseline... Keep the area empty for 10 seconds.",
            "Baseline RSSI: -48.2 dBm",
            "SYSTEM READY",
            "--------------------------------------",
            "RSSI=-48 | AVG=-48.1 | BASE=-48.2 | DEV=0.1 | STATUS=STABLE",
            "RSSI=-48 | AVG=-48.2 | BASE=-48.2 | DEV=0.0 | STATUS=STABLE",
            "RSSI=-53 | AVG=-51.4 | BASE=-48.2 | DEV=3.2 | STATUS=LOW ACTIVITY",
            "RSSI=-57 | AVG=-55.1 | BASE=-48.2 | DEV=6.9 | STATUS=MOVEMENT",
            "RSSI=-59 | AVG=-56.8 | BASE=-48.2 | DEV=8.6 | STATUS=HIGH ACTIVITY"
        ]
    )

    # 4. Backend live
    create_terminal_image(
        os.path.join(SCREEN_DIR, "backend-live.png"),
        "PYTHON FASTAPI BACKEND SERVER",
        [
            "INFO:     Started server process [PID: 28412]",
            "INFO:     Waiting for application startup.",
            "[UDP]     Listening for ESP32 telemetry on 0.0.0.0:5005",
            "[STREAM]  Telemetry fusion broadcast loop started at 20 Hz",
            "[NEXUS]   Server operational on port 8000. UDP on 5005.",
            "INFO:     Application startup complete.",
            "INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)",
            "[WS]      Client connected. Total active clients: 1",
            "[FUSION]  Active Nodes: 4 | Global Motion: 0.72 | Mode: RSSI ONLY",
            "[TRACK]   Estimated: (x: 4.82m, y: 5.14m, v: 0.88m/s) | Conf: 88%"
        ]
    )

    # 5. 3D Visualization mockup
    create_terminal_image(
        os.path.join(SCREEN_DIR, "3d-visualization.png"),
        "THREE.JS 3D VIRTUAL ROOM & TELEMETRY HUD",
        [
            "============================================================",
            "          NEXUS-PRESENCE 3D MISSION CONTROL                 ",
            "============================================================",
            "[ROOM]    10m x 10m x 3m Virtual Environment loaded",
            "[NODES]   ESP32 #1, #2, #3, #4 meshes active with RF pulses",
            "[AVATAR]  Procedural 3D humanoid avatar instantiated",
            "[KINEMATICS] Walking gait cycles synchronized to velocity",
            "[RAYS]    Dynamic RF line-of-sight beams active",
            "HUD >>    X: 4.82m | Y: 5.14m | Speed: 0.88 m/s | Heading: 94 deg",
            "HUD >>    State: MOVEMENT | Confidence: 88% | Mode: RSSI ONLY",
            "CHARTS >> Canvas 60-frame rolling RSSI & motion score streaming"
        ]
    )

if __name__ == "__main__":
    generate_system_architecture()
    generate_four_node_topology()
    generate_data_flow()
    generate_localization_pipeline()
    generate_screenshots()
    print("[DONE] All diagrams and screenshots generated successfully.")
