"""
Multi-Node Signal Fusion Engine
Author: Uday Kiran Jammula
"""

import time
from typing import Dict, List, Tuple
from backend.models.telemetry import ProcessedNodeState
from backend.config import config

class SignalFusionEngine:
    """
    Fuses asynchronous RF disturbance metrics across all 4 nodes to produce
    a unified global presence assessment and node weighting profile.
    """
    def __init__(self):
        self.node_states: Dict[int, ProcessedNodeState] = {}

    def update_node(self, state: ProcessedNodeState):
        self.node_states[state.node_id] = state

    def fuse(self) -> Tuple[float, str, Dict[int, float], str]:
        """
        Fuses current node telemetry.
        Returns:
            (global_motion_score, global_status, node_spatial_weights, sensing_mode_label)
        """
        now = time.time()
        active_nodes = [
            s for s in self.node_states.values()
            if (now - s.last_seen_epoch) < 5.0
        ]

        if not active_nodes:
            return 0.0, "STABLE", {n: 0.25 for n in [1, 2, 3, 4]}, "RSSI ONLY"

        # Check if any node is streaming CSI
        csi_active = any(s.sensing_mode == "CSI_RSSI" for s in active_nodes)
        sensing_mode_label = "CSI + RSSI" if csi_active else "RSSI ONLY"

        # Global motion score is weighted maximum of active nodes
        motion_scores = [s.motion_score for s in active_nodes]
        global_score = max(motion_scores)

        # Classify global system status based on highest disturbance
        deviations = [s.deviation for s in active_nodes]
        max_dev = max(deviations) if deviations else 0.0

        if max_dev < config.STABLE_THRESHOLD:
            global_status = "STABLE"
        elif max_dev < config.LOW_ACTIVITY_THRESHOLD:
            global_status = "LOW ACTIVITY"
        elif max_dev < config.MOVEMENT_THRESHOLD:
            global_status = "MOVEMENT"
        else:
            global_status = "HIGH ACTIVITY"

        # Calculate spatial proximity weights for localization
        # Nodes observing higher deviation and variance are assigned higher weight
        weights: Dict[int, float] = {}
        total_weight = 0.0

        for nid in [1, 2, 3, 4]:
            if nid in self.node_states and (now - self.node_states[nid].last_seen_epoch) < 5.0:
                s = self.node_states[nid]
                # Base weight + perturbation response
                w = 1.0 + (s.deviation * 1.5) + (s.motion_score * 3.0)
            else:
                w = 0.2  # Unseen or offline node has low weight
            weights[nid] = w
            total_weight += w

        # Normalize weights
        for nid in weights:
            weights[nid] = weights[nid] / total_weight if total_weight > 0 else 0.25

        return round(global_score, 3), global_status, weights, sensing_mode_label
