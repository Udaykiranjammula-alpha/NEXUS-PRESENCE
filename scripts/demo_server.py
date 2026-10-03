"""
Standalone Demo Simulation Server
Simulates human motion trajectories and generates realistic multi-node RF perturbations.
Author: Uday Kiran Jammula
"""

import sys
import os
import time
import math
import json
import socket
import random

UDP_HOST = "127.0.0.1"
UDP_PORT = 5005
ROOM_WIDTH = 10.0
ROOM_LENGTH = 10.0

NODE_POSITIONS = {
    1: (0.0, 0.0),    # Master Node
    2: (10.0, 0.0),   # Sensor Node A
    3: (0.0, 10.0),   # Sensor Node B
    4: (10.0, 10.0),  # Sensor Node C
}

BASELINES = {1: -45.0, 2: -48.0, 3: -46.0, 4: -50.0}

def generate_trajectory(t: float):
    """Generates complex realistic human walk with pauses and turns."""
    # Phase cycle: walk (0-20s), pause (20-25s), fast walk (25-40s), turn around
    cycle = t % 40.0
    
    if 20.0 <= cycle <= 25.0:
        # Stationary / subtle fidgeting
        x = 5.0 + 0.05 * math.sin(t * 3.0)
        y = 5.0 + 0.05 * math.cos(t * 2.5)
        state = "STABLE"
        speed = 0.05
    elif 25.0 < cycle <= 40.0:
        # Active transit along perimeter
        progress = (cycle - 25.0) / 15.0
        angle = progress * 2.0 * math.pi
        x = 5.0 + 3.5 * math.cos(angle)
        y = 5.0 + 3.5 * math.sin(angle)
        state = "HIGH ACTIVITY"
        speed = 1.35
    else:
        # Standard walking across room diagonal
        progress = cycle / 20.0
        x = 2.0 + 6.0 * progress
        y = 3.0 + 4.0 * math.sin(progress * math.pi)
        state = "MOVEMENT"
        speed = 0.85

    return x, y, state, speed

def simulate_node_rssi(nid: int, person_x: float, person_y: float, state: str):
    nx, ny = NODE_POSITIONS[nid]
    dist = math.sqrt((person_x - nx) ** 2 + (person_y - ny) ** 2)
    
    # Multipath and RF shadowing when human intersects line-of-sight
    base = BASELINES[nid]
    # Human body RF attenuation (3 - 8 dB drop when close)
    proximity_attenuation = 7.0 / (dist + 1.0)
    
    noise = random.gauss(0.0, 0.6 if state == "STABLE" else 1.8)
    sim_rssi = int(base - proximity_attenuation + noise)
    deviation = abs(sim_rssi - base)
    
    return sim_rssi, deviation

def main():
    print("==================================================")
    print("      NEXUS-PRESENCE: DEMO SIMULATION SERVER      ")
    print("               [SIMULATION MODE ACTIVE]           ")
    print("          Author: Uday Kiran Jammula              ")
    print("==================================================")
    print(f"Target UDP Destination: {UDP_HOST}:{UDP_PORT}")
    print("Simulating realistic human transit trajectories across 4 nodes.")
    print("Press Ctrl+C to terminate simulation.\n")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    t = 0.0
    packet_seq = 0

    try:
        while True:
            t += 0.1
            packet_seq += 1
            px, py, state, speed = generate_trajectory(t)

            # Generate and dispatch telemetry for all 4 nodes
            for nid in [1, 2, 3, 4]:
                rssi, dev = simulate_node_rssi(nid, px, py, state)
                role = "MASTER" if nid == 1 else f"SENSOR_{chr(64 + nid - 1)}"
                
                # Format standard packet
                pkt = {
                    "node_id": nid,
                    "role": role,
                    "timestamp": int(time.time() * 1000),
                    "rssi": rssi,
                    "channel": 6,
                    "packet_count": packet_seq,
                    "motion_score": round(min(max(dev / 8.0, 0.0), 1.0), 2),
                    "average_rssi": round(float(rssi), 1),
                    "baseline": BASELINES[nid],
                    "deviation": round(dev, 1),
                    "variance": round(1.2 + (0.8 if state != 'STABLE' else 0.0), 2),
                    "status": state,
                    "sensing_mode": "RSSI_ONLY"
                }

                data_bytes = json.dumps(pkt).encode("utf-8")
                sock.sendto(data_bytes, (UDP_HOST, UDP_PORT))

            if packet_seq % 10 == 0:
                print(f"[SIM] Pos: ({px:.2f}m, {py:.2f}m) | State: {state:<13} | Speed: {speed:.2f}m/s | Pkts: {packet_seq * 4}")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n[SIM] Demo simulation stopped.")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
