"""
Telemetry and State Data Models
Author: Uday Kiran Jammula
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class RawNodeTelemetry(BaseModel):
    node_id: int
    role: Optional[str] = "SENSOR"
    timestamp: int
    rssi: int
    channel: Optional[int] = 6
    packet_count: Optional[int] = 0
    motion_score: Optional[float] = 0.0
    average_rssi: Optional[float] = None
    baseline: Optional[float] = None
    deviation: Optional[float] = None
    variance: Optional[float] = None
    status: Optional[str] = "STABLE"
    sensing_mode: Optional[str] = "RSSI_ONLY"
    csi_subcarriers: Optional[int] = 0
    csi_variance: Optional[float] = 0.0
    csi_amplitude: Optional[List[int]] = Field(default_factory=list)
    csi_phase: Optional[List[int]] = Field(default_factory=list)

class ProcessedNodeState(BaseModel):
    node_id: int
    role: str
    online: bool
    last_seen_epoch: float
    raw_rssi: int
    filtered_rssi: float
    baseline_rssi: float
    deviation: float
    variance: float
    motion_score: float
    status: str
    sensing_mode: str
    packet_rate: float
    total_packets: int

class EstimatedPosition(BaseModel):
    x: float
    y: float
    z: float
    velocity: float
    direction: float  # radians (0 to 2*pi)
    movement: str     # STABLE, LOW ACTIVITY, MOVEMENT, HIGH ACTIVITY
    confidence: float # 0.0 to 1.0

class FusionTelemetryPacket(BaseModel):
    system_status: str # ONLINE, DEGRADED, CALIBRATING, SIMULATION
    timestamp: float
    sensing_mode: str  # "CSI + RSSI" or "RSSI ONLY"
    global_motion_score: float
    global_status: str
    position_estimate: EstimatedPosition
    nodes: Dict[int, ProcessedNodeState]
    is_simulation: bool = False
