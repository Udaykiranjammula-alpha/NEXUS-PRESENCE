"""
FastAPI Server & Central Telemetry Pipeline
Author: Uday Kiran Jammula
"""

import os
import sys
import time
import asyncio
import logging
from typing import Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Ensure root directory is on PYTHONPATH
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.config import config
from backend.models.telemetry import (
    RawNodeTelemetry, ProcessedNodeState, EstimatedPosition, FusionTelemetryPacket
)
from backend.processing.rssi_processor import RSSIProcessor
from backend.processing.csi_processor import CSIProcessor
from backend.processing.motion_detector import MotionDetector
from backend.processing.signal_fusion import SignalFusionEngine
from backend.localization.position_estimator import PositionEstimator
from backend.server.websocket_server import ws_manager
from backend.server.udp_receiver import start_udp_listener

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("nexus.main")

# State & Engine Singletons
rssi_processors: Dict[int, RSSIProcessor] = {
    nid: RSSIProcessor(node_id=nid, window_size=config.WINDOW_SIZE) for nid in [1, 2, 3, 4]
}
csi_processors: Dict[int, CSIProcessor] = {
    nid: CSIProcessor(node_id=nid) for nid in [1, 2, 3, 4]
}
motion_detectors: Dict[int, MotionDetector] = {
    nid: MotionDetector() for nid in [1, 2, 3, 4]
}
fusion_engine = SignalFusionEngine()
position_estimator = PositionEstimator()

node_states: Dict[int, ProcessedNodeState] = {}
packet_counts: Dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0}
last_packet_times: Dict[int, float] = {}

simulation_active: bool = False
simulation_time: float = 0.0

def process_raw_telemetry(raw: RawNodeTelemetry):
    """Processes incoming telemetry from physical ESP32 or serial bridge."""
    nid = raw.node_id
    if nid not in rssi_processors:
        rssi_processors[nid] = RSSIProcessor(node_id=nid, window_size=config.WINDOW_SIZE)
        csi_processors[nid] = CSIProcessor(node_id=nid)
        motion_detectors[nid] = MotionDetector()

    now = time.time()
    packet_counts[nid] = packet_counts.get(nid, 0) + 1
    last_packet_times[nid] = now

    # 1. Process RSSI
    filtered_rssi, avg_rssi, dev, var = rssi_processors[nid].process(raw.rssi)

    # 2. Process CSI if available
    csi_metrics = csi_processors[nid].process(raw.csi_amplitude, raw.csi_phase)
    csi_factor = csi_metrics.get("csi_motion_factor", 0.0)

    # 3. Detect motion state
    status, score = motion_detectors[nid].classify(dev, var, csi_factor)

    role_str = "MASTER" if nid == 1 else f"SENSOR_{chr(64 + nid - 1)}"
    sensing_mode = "CSI_RSSI" if csi_metrics.get("csi_supported", False) else "RSSI_ONLY"

    state = ProcessedNodeState(
        node_id=nid,
        role=role_str,
        online=True,
        last_seen_epoch=now,
        raw_rssi=raw.rssi,
        filtered_rssi=round(filtered_rssi, 1),
        baseline_rssi=round(rssi_processors[nid].baseline or raw.rssi, 1),
        deviation=round(dev, 2),
        variance=round(var, 2),
        motion_score=score,
        status=status,
        sensing_mode=sensing_mode,
        packet_rate=10.0,
        total_packets=packet_counts[nid]
    )

    node_states[nid] = state
    fusion_engine.update_node(state)


async def telemetry_broadcast_loop():
    """High-frequency (20 Hz) fusion and WebSocket broadcast loop."""
    global simulation_active, simulation_time
    logger.info("[STREAM] Telemetry fusion broadcast loop started at 20 Hz.")

    while True:
        try:
            now = time.time()

            # Handle simulation mode if active or when no physical nodes are transmitting
            if simulation_active:
                simulation_time += 0.05
                # Synthetic walk path in 10x10m room: figure-8 trajectory
                sim_x = 5.0 + 3.2 * (math_sin := __import__("math").sin(simulation_time * 0.5))
                sim_y = 5.0 + 2.8 * __import__("math").sin(simulation_time * 1.0)
                sim_speed = 0.85 + 0.15 * __import__("math").cos(simulation_time * 0.8)
                sim_dir = __import__("math").atan2(__import__("math").cos(simulation_time * 1.0) * 2.8, math_sin * 1.6)
                if sim_dir < 0:
                    sim_dir += 2 * 3.14159

                sim_state = "MOVEMENT" if sim_speed > 0.4 else "LOW ACTIVITY"

                # Simulate RSSI perturbations on the 4 corner nodes
                for nid, npos in [(1, (0,0)), (2, (10,0)), (3, (0,10)), (4, (10,10))]:
                    dist = __import__("math").sqrt((sim_x - npos[0])**2 + (sim_y - npos[1])**2)
                    sim_rssi = int(-42.0 - 10.0 * 2.4 * __import__("math").log10(max(dist, 0.5)) + (time.time() % 1.0 - 0.5) * 1.5)
                    node_states[nid] = ProcessedNodeState(
                        node_id=nid,
                        role="MASTER" if nid == 1 else f"SENSOR_{chr(64 + nid - 1)}",
                        online=True,
                        last_seen_epoch=now,
                        raw_rssi=sim_rssi,
                        filtered_rssi=float(sim_rssi),
                        baseline_rssi=-48.0,
                        deviation=round(abs(sim_rssi - (-48.0)), 1),
                        variance=1.8,
                        motion_score=round(min(max(sim_speed / 1.5, 0.1), 0.95), 2),
                        status=sim_state,
                        sensing_mode="RSSI_ONLY",
                        packet_rate=15.0,
                        total_packets=100 + int(simulation_time * 10)
                    )

                pos_est = EstimatedPosition(
                    x=round(sim_x, 2),
                    y=round(sim_y, 2),
                    z=0.0,
                    velocity=round(sim_speed, 2),
                    direction=round(sim_dir, 2),
                    movement=sim_state,
                    confidence=0.88
                )
                global_score = round(min(max(sim_speed / 1.5, 0.1), 0.95), 2)
                global_status = sim_state
                sensing_mode = "RSSI ONLY (SIMULATION)"
            else:
                # Actual physical sensor multi-node fusion
                global_score, global_status, weights, sensing_mode = fusion_engine.fuse()
                pos_est = position_estimator.update(
                    node_states=node_states,
                    node_weights=weights,
                    global_status=global_status,
                    is_simulation=False
                )

            # Check online status of nodes (offline if no packet in 3 seconds)
            for nid in [1, 2, 3, 4]:
                if nid in node_states:
                    is_alive = (now - node_states[nid].last_seen_epoch) < 3.0 or simulation_active
                    node_states[nid].online = is_alive

            packet = FusionTelemetryPacket(
                system_status="ONLINE" if (any(s.online for s in node_states.values()) or simulation_active) else "STANDBY",
                timestamp=now,
                sensing_mode=sensing_mode,
                global_motion_score=global_score,
                global_status=global_status,
                position_estimate=pos_est,
                nodes=node_states,
                is_simulation=simulation_active
            )

            await ws_manager.broadcast_json(packet.model_dump())
            await asyncio.sleep(0.05)  # 20 Hz refresh rate
        except Exception as e:
            logger.error(f"[STREAM] Broadcast error: {e}", exc_info=True)
            await asyncio.sleep(0.1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start UDP socket listener and broadcast loop
    udp_transport, _ = await start_udp_listener(
        config.BACKEND_HOST,
        config.UDP_PORT,
        process_raw_telemetry
    )
    broadcast_task = asyncio.create_task(telemetry_broadcast_loop())
    logger.info(f"[NEXUS] Server operational on port {config.BACKEND_PORT}. UDP on {config.UDP_PORT}.")
    
    yield
    
    # Shutdown
    broadcast_task.cancel()
    if udp_transport:
        udp_transport.close()
    logger.info("[NEXUS] Server shutting down cleanly.")


app = FastAPI(
    title="NEXUS-PRESENCE Telemetry Server",
    description="Multi-Node Ambient Wi-Fi Human Presence & 3D Localization Engine",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST Endpoints
@app.get("/api/status")
async def get_system_status():
    return {
        "project": config.PROJECT_NAME,
        "author": config.AUTHOR,
        "active_clients": len(ws_manager.active_connections),
        "simulation_active": simulation_active,
        "nodes_registered": len(node_states),
        "room_dimensions": {
            "width": config.ROOM_WIDTH,
            "length": config.ROOM_LENGTH,
            "height": config.ROOM_HEIGHT
        }
    }

@app.get("/api/config")
async def get_configuration():
    return {
        "room": {
            "width": config.ROOM_WIDTH,
            "length": config.ROOM_LENGTH,
            "height": config.ROOM_HEIGHT
        },
        "nodes": {
            nid: {"id": n.id, "label": n.label, "position": n.position}
            for nid, n in config.NODES.items()
        },
        "thresholds": {
            "stable": config.STABLE_THRESHOLD,
            "low_activity": config.LOW_ACTIVITY_THRESHOLD,
            "movement": config.MOVEMENT_THRESHOLD
        }
    }

@app.post("/api/telemetry")
async def ingest_telemetry(packet: RawNodeTelemetry):
    process_raw_telemetry(packet)
    return {"status": "accepted", "node_id": packet.node_id}

@app.post("/api/calibrate")
async def calibrate_baseline():
    for nid, proc in rssi_processors.items():
        if proc.raw_history:
            proc.calibrate(list(proc.raw_history))
    return {"status": "calibrated", "timestamp": time.time()}

@app.post("/api/demo/toggle")
async def toggle_demo_mode():
    global simulation_active
    simulation_active = not simulation_active
    logger.info(f"[MODE] Demo / Simulation mode toggled: {simulation_active}")
    return {"simulation_active": simulation_active}

# WebSocket Endpoint
@app.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep-alive ping/pong
            msg = await websocket.receive_text()
            if msg == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        ws_manager.disconnect(websocket)

# Static file serving
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
VISUALIZATION_DIR = os.path.join(PROJECT_ROOT, "visualization")

if os.path.exists(FRONTEND_DIR):
    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")
if os.path.exists(VISUALIZATION_DIR):
    app.mount("/visualization", StaticFiles(directory=VISUALIZATION_DIR), name="visualization")

@app.get("/")
async def root_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "NEXUS-PRESENCE API is running. Access /dashboard for telemetry."}

@app.get("/dashboard")
async def dashboard_page():
    dash_path = os.path.join(FRONTEND_DIR, "dashboard.html")
    if os.path.exists(dash_path):
        return FileResponse(dash_path)
    raise HTTPException(status_code=404, detail="Dashboard template not found")
