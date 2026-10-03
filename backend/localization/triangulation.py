"""
Multilateration & RF Disturbance Triangulation
Author: Uday Kiran Jammula
"""

import math
from typing import Dict, Tuple, List
import numpy as np
from backend.config import config
from backend.localization.coordinate_system import CoordinateSystem

class TriangulationEngine:
    """
    Computes spatial coordinate estimates using a hybrid model:
    1. Log-Distance Path Loss (LDPL) range estimation
    2. Weighted Centroid Localization (WCL) based on RF disturbance gradients
    3. Non-linear least-squares residual minimization
    """
    def __init__(self, coord_sys: CoordinateSystem):
        self.coord_sys = coord_sys
        self.path_loss_n = config.PATH_LOSS_EXPONENT_N
        self.rssi_1m = config.REFERENCE_RSSI_1M

    def rssi_to_distance(self, rssi: float) -> float:
        """
        Inverts Log-Distance Path Loss Model:
        RSSI = RSSI_0 - 10 * n * log10(d)  =>  d = 10 ^ ((RSSI_0 - RSSI) / (10 * n))
        """
        # Constrain RSSI to valid domain
        r = min(max(rssi, -95.0), -15.0)
        exponent = (self.rssi_1m - r) / (10.0 * self.path_loss_n)
        dist = 10.0 ** exponent
        return max(0.5, min(dist, 15.0))

    def estimate_position_wcl(self, weights: Dict[int, float]) -> Tuple[float, float, float]:
        """
        Weighted Centroid Localization based on normalized disturbance weights.
        Useful when human presence acts as an RF attenuator / scatterer.
        """
        sum_x = 0.0
        sum_y = 0.0
        sum_w = 0.0

        for nid, w in weights.items():
            pos = self.coord_sys.get_node_position(nid)
            sum_x += pos[0] * w
            sum_y += pos[1] * w
            sum_w += w

        if sum_w == 0.0:
            return self.coord_sys.width / 2.0, self.coord_sys.length / 2.0, 0.0

        raw_x = sum_x / sum_w
        raw_y = sum_y / sum_w

        return self.coord_sys.clamp_to_bounds(raw_x, raw_y, 0.0)

    def multilaterate_least_squares(
        self,
        node_ranges: Dict[int, float],
        initial_guess: Tuple[float, float]
    ) -> Tuple[float, float]:
        """
        Non-linear least squares solver minimizing sum((norm(p - anchor_i) - d_i)^2).
        """
        anchors = []
        dists = []

        for nid, d in node_ranges.items():
            pos = self.coord_sys.get_node_position(nid)
            anchors.append([pos[0], pos[1]])
            dists.append(d)

        if len(anchors) < 3:
            return initial_guess

        anchors_np = np.array(anchors, dtype=np.float64)
        dists_np = np.array(dists, dtype=np.float64)

        # Gradient descent optimization
        p = np.array(initial_guess, dtype=np.float64)
        lr = 0.08
        
        for _ in range(25):
            diffs = p - anchors_np
            calculated_dists = np.linalg.norm(diffs, axis=1) + 1e-6
            residuals = calculated_dists - dists_np
            
            # Gradients: sum( (dist_calc - dist_meas) * (p - a_i) / dist_calc )
            unit_vectors = diffs / calculated_dists[:, np.newaxis]
            grad = np.sum(residuals[:, np.newaxis] * unit_vectors, axis=0)
            
            p -= lr * grad

        clamped = self.coord_sys.clamp_to_bounds(float(p[0]), float(p[1]), 0.0)
        return clamped[0], clamped[1]
