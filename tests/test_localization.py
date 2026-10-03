"""
Unit Tests for 3D Localization, Coordinates, and Confidence
Author: Uday Kiran Jammula
"""

import pytest
from backend.localization.coordinate_system import CoordinateSystem
from backend.localization.triangulation import TriangulationEngine
from backend.localization.confidence import ConfidenceEngine
from backend.localization.position_estimator import PositionEstimator
from backend.models.telemetry import ProcessedNodeState
import time

def test_coordinate_system_clamping():
    cs = CoordinateSystem(width=10.0, length=10.0, height=3.0)
    # Inside bounds
    cx, cy, cz = cs.clamp_to_bounds(5.0, 5.0, 1.0)
    assert cx == 5.0 and cy == 5.0 and cz == 1.0

    # Outside bounds
    cx, cy, cz = cs.clamp_to_bounds(-5.0, 15.0, 4.0)
    assert cx == 0.3
    assert cy == 9.7
    assert cz == 3.0

def test_triangulation_rssi_to_distance():
    cs = CoordinateSystem()
    tri = TriangulationEngine(cs)
    d1 = tri.rssi_to_distance(-42.0)
    # At reference RSSI (-42 dBm), distance should be around 1.0 meter
    assert pytest.approx(d1, 0.1) == 1.0
    
    # Weaker RSSI should produce larger distance
    d2 = tri.rssi_to_distance(-65.0)
    assert d2 > d1

def test_confidence_engine():
    conf_4_nodes = ConfidenceEngine.compute_confidence(4, residuals=0.5, avg_variance=0.2)
    conf_2_nodes = ConfidenceEngine.compute_confidence(2, residuals=0.5, avg_variance=0.2)
    assert conf_4_nodes > conf_2_nodes
    assert 0.0 <= conf_4_nodes <= 1.0

def test_position_estimator_tracking():
    estimator = PositionEstimator()
    now = time.time()
    
    # Simulate high disturbance near Node 2 (10, 0)
    weights = {1: 0.1, 2: 0.7, 3: 0.1, 4: 0.1}
    node_states = {
        2: ProcessedNodeState(
            node_id=2, role="SENSOR_A", online=True, last_seen_epoch=now,
            raw_rssi=-48, filtered_rssi=-48.0, baseline_rssi=-40.0,
            deviation=8.0, variance=2.5, motion_score=0.8,
            status="MOVEMENT", sensing_mode="RSSI_ONLY",
            packet_rate=10.0, total_packets=100
        )
    }

    pos = estimator.update(node_states, weights, global_status="MOVEMENT")
    assert pos.x > 5.0  # Should be pulled towards Node 2's side
    assert pos.confidence > 0.0
