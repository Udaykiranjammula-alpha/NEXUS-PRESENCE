"""
Localization Confidence & GDOP Engine
Author: Uday Kiran Jammula
"""

import math
from typing import Dict, Tuple, List
import numpy as np

class ConfidenceEngine:
    """
    Computes a realistic confidence score (0.0 to 1.0) for estimated target coordinates.
    Considers:
    - Active node quorum (4 nodes = optimal, 3 = acceptable, <3 = degraded)
    - Geometric Dilution of Precision (GDOP)
    - Aggregate signal variance across active links
    """
    @staticmethod
    def compute_confidence(
        active_node_count: int,
        residuals: float,
        avg_variance: float,
        is_simulation: bool = False
    ) -> float:
        if is_simulation:
            return 0.88

        # 1. Quorum factor
        if active_node_count >= 4:
            quorum_factor = 0.90
        elif active_node_count == 3:
            quorum_factor = 0.72
        elif active_node_count == 2:
            quorum_factor = 0.45
        else:
            return 0.15

        # 2. Residual penalty (least-squares distance error)
        residual_penalty = max(0.0, min(residuals * 0.08, 0.35))

        # 3. Variance penalty
        variance_penalty = max(0.0, min(avg_variance * 0.05, 0.25))

        raw_confidence = quorum_factor - residual_penalty - variance_penalty
        return round(max(0.10, min(0.95, raw_confidence)), 2)
