"""
Centralized Configuration for NEXUS-PRESENCE
Author: Uday Kiran Jammula
"""

import os
from typing import Dict, Tuple
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class NodeConfig(BaseModel):
    id: int
    label: str
    position: Tuple[float, float, float]  # (x, y, z) in meters

class SystemConfig:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "NEXUS-PRESENCE")
    AUTHOR: str = os.getenv("AUTHOR", "Uday Kiran Jammula")
    
    # Network Parameters
    WIFI_SSID: str = os.getenv("WIFI_SSID", "NEXUS_PRESENCE")
    WIFI_PASSWORD: str = os.getenv("WIFI_PASSWORD", "nexus123")
    MASTER_IP: str = os.getenv("MASTER_IP", "192.168.4.1")
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    UDP_PORT: int = int(os.getenv("UDP_PORT", "5005"))
    WS_PORT: int = int(os.getenv("WS_PORT", "8000"))
    
    # Room Dimensions in Meters
    ROOM_WIDTH: float = float(os.getenv("ROOM_WIDTH", "10.0"))
    ROOM_LENGTH: float = float(os.getenv("ROOM_LENGTH", "10.0"))
    ROOM_HEIGHT: float = float(os.getenv("ROOM_HEIGHT", "3.0"))
    
    # 4 Node Anchor Positions (X, Y, Z in meters)
    # Master node at origin (0,0), Nodes spaced across corners
    NODES: Dict[int, NodeConfig] = {
        1: NodeConfig(id=1, label="MASTER_NODE", position=(0.0, 0.0, 2.0)),
        2: NodeConfig(id=2, label="SENSOR_NODE_A", position=(10.0, 0.0, 2.0)),
        3: NodeConfig(id=3, label="SENSOR_NODE_B", position=(0.0, 10.0, 2.0)),
        4: NodeConfig(id=4, label="SENSOR_NODE_C", position=(10.0, 10.0, 2.0)),
    }
    
    # Signal Processing Hyperparameters
    WINDOW_SIZE: int = int(os.getenv("WINDOW_SIZE", "10"))
    STABLE_THRESHOLD: float = float(os.getenv("STABLE_THRESHOLD", "2.0"))
    LOW_ACTIVITY_THRESHOLD: float = float(os.getenv("LOW_ACTIVITY_THRESHOLD", "4.0"))
    MOVEMENT_THRESHOLD: float = float(os.getenv("MOVEMENT_THRESHOLD", "7.0"))
    
    # Log-Distance Path Loss Parameters for Trilateration
    # RSSI = RSSI_0 - 10 * n * log10(d)
    PATH_LOSS_EXPONENT_N: float = 2.4
    REFERENCE_RSSI_1M: float = -42.0

config = SystemConfig()
