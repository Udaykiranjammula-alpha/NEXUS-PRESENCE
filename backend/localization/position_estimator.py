"""
Position Estimator & Temporal Tracking Filter
Author: Uday Kiran Jammula
"""

import time
import math
from typing import Dict, Tuple, Optional
from backend.config import config
from backend.models.telemetry import EstimatedPosition, ProcessedNodeState
from backend.localization.coordinate_system import CoordinateSystem
from backend.localization.triangulation import TriangulationEngine
from backend.localization.confidence import ConfidenceEngine

class PositionEstimator:
    """
    Main localization coordinator. Integrates multi-node weights, multilateration,
    temporal filtering, velocity estimation, and confidence scoring.
    """
    def __init__(self, coord_sys: Optional[CoordinateSystem] = None):
        self.coord_sys = coord_sys or CoordinateSystem()
        self.triangulation = TriangulationEngine(self.coord_sys)
        self.confidence_engine = ConfidenceEngine()

        # State tracking
        self.current_x = self.coord_sys.width / 2.0
        self.current_y = self.coord_sys.length / 2.0
        self.current_z = 0.0
        self.last_update_time = time.time()
        self.velocity = 0.0
        self.direction = 0.0
        self.smoothing_factor = 0.30  # Low-pass alpha for position smoothing

    def update(
        self,
        node_states: Dict[int, ProcessedNodeState],
        node_weights: Dict[int, float],
        global_status: str,
        is_simulation: bool = False
    ) -> EstimatedPosition:
        now = time.time()
        dt = max(now - self.last_update_time, 0.01)
        self.last_update_time = now

        active_nodes = [
            s for s in node_states.values()
            if (now - s.last_seen_epoch) < 5.0
        ]

        if not active_nodes and not is_simulation:
            # Idle default when no signals active
            return EstimatedPosition(
                x=round(self.current_x, 2),
                y=round(self.current_y, 2),
                z=0.0,
                velocity=0.0,
                direction=self.direction,
                movement="STABLE",
                confidence=0.10
            )

        # 1. Compute raw position using disturbance centroid
        raw_x, raw_y, _ = self.triangulation.estimate_position_wcl(node_weights)

        # 2. Refine position if at least 3 nodes are active using multilateration
        if len(active_nodes) >= 3:
            ranges = {
                s.node_id: self.triangulation.rssi_to_distance(s.filtered_rssi)
                for s in active_nodes
            }
            ls_x, ls_y = self.triangulation.multilaterate_least_squares(
                ranges, (raw_x, raw_y)
            )
            # Blend centroid with least-squares
            target_x = 0.6 * raw_x + 0.4 * ls_x
            target_y = 0.6 * raw_y + 0.4 * ls_y
        else:
            target_x, target_y = raw_x, raw_y

        # 3. Apply temporal low-pass filter to prevent teleportation
        new_x = self.smoothing_factor * target_x + (1.0 - self.smoothing_factor) * self.current_x
        new_y = self.smoothing_factor * target_y + (1.0 - self.smoothing_factor) * self.current_y
        new_x, new_y, _ = self.coord_sys.clamp_to_bounds(new_x, new_y, 0.0)

        # 4. Compute velocity and heading angle
        dx = new_x - self.current_x
        dy = new_y - self.current_y
        dist_moved = math.sqrt(dx * dx + dy * dy)
        instant_velocity = dist_moved / dt

        # Smooth velocity
        self.velocity = 0.35 * instant_velocity + 0.65 * self.velocity

        if dist_moved > 0.05:
            # Update heading direction only if movement is significant
            self.direction = math.atan2(dy, dx)
            if self.direction < 0:
                self.direction += 2 * math.pi

        self.current_x = new_x
        self.current_y = new_y

        # 5. Determine movement state
        if global_status == "STABLE" or self.velocity < 0.12:
            movement_state = "STABLE"
        elif self.velocity < 0.45 or global_status == "LOW ACTIVITY":
            movement_state = "LOW ACTIVITY"
        elif self.velocity < 1.3 or global_status == "MOVEMENT":
            movement_state = "MOVEMENT"
        else:
            movement_state = "HIGH ACTIVITY"

        # 6. Compute confidence
        variances = [s.variance for s in active_nodes]
        avg_var = sum(variances) / len(variances) if variances else 0.5
        conf = self.confidence_engine.compute_confidence(
            active_node_count=len(active_nodes),
            residuals=0.8,
            avg_variance=avg_var,
            is_simulation=is_simulation
        )

        return EstimatedPosition(
            x=round(self.current_x, 2),
            y=round(self.current_y, 2),
            z=0.0,
            velocity=round(self.velocity, 2),
            direction=round(self.direction, 2),
            movement=movement_state,
            confidence=conf
        )
