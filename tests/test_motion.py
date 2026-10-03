"""
Unit Tests for Motion Detection & Classification States
Author: Uday Kiran Jammula
"""

import pytest
from backend.processing.motion_detector import MotionDetector
from backend.processing.signal_fusion import SignalFusionEngine
from backend.models.telemetry import ProcessedNodeState
import time

def test_motion_detector_states():
    md = MotionDetector(
        stable_threshold=2.0,
        low_activity_threshold=4.0,
        movement_threshold=7.0
    )

    # 1. Stable
    state, score = md.classify(deviation=0.5, variance=0.2)
    assert state == "STABLE"
    assert score < 0.1

    # 2. Low activity
    state, score = md.classify(deviation=2.5, variance=1.5)
    assert state == "LOW ACTIVITY"

    # 3. Movement
    state, score = md.classify(deviation=5.0, variance=2.5)
    assert state == "MOVEMENT"

    # 4. High activity
    state, score = md.classify(deviation=9.0, variance=4.0)
    assert state == "HIGH ACTIVITY"
    assert score > 0.5

def test_signal_fusion_engine():
    engine = SignalFusionEngine()
    now = time.time()

    state_node2 = ProcessedNodeState(
        node_id=2, role="SENSOR_A", online=True, last_seen_epoch=now,
        raw_rssi=-48, filtered_rssi=-48.0, baseline_rssi=-45.0,
        deviation=3.0, variance=1.5, motion_score=0.4,
        status="LOW ACTIVITY", sensing_mode="RSSI_ONLY",
        packet_rate=10.0, total_packets=50
    )
    engine.update_node(state_node2)

    score, global_status, weights, sensing_mode = engine.fuse()
    assert global_status in ["LOW ACTIVITY", "STABLE", "MOVEMENT"]
    assert 2 in weights
    assert sensing_mode == "RSSI ONLY"
