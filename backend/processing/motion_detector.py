"""
Motion Detection and State Classifier
Author: Uday Kiran Jammula
"""

from typing import Tuple, Dict, Any
from backend.config import config

class MotionDetector:
    """
    Classifies RF signal disturbance into human presence/movement states:
    - STABLE: Static environment, no human disturbance detected.
    - LOW_ACTIVITY: Subtle or localized movement (breathing, typing, micro-gestures).
    - MOVEMENT: Active human transit or limb motion crossing RF Fresnel zones.
    - HIGH_ACTIVITY: Rapid movement, rapid pacing, or multi-person transit.
    """
    def __init__(
        self,
        stable_threshold: float = config.STABLE_THRESHOLD,
        low_activity_threshold: float = config.LOW_ACTIVITY_THRESHOLD,
        movement_threshold: float = config.MOVEMENT_THRESHOLD,
    ):
        self.stable_threshold = stable_threshold
        self.low_activity_threshold = low_activity_threshold
        self.movement_threshold = movement_threshold

    def classify(self, deviation: float, variance: float, csi_motion_factor: float = 0.0) -> Tuple[str, float]:
        """
        Classifies motion based on deviation, variance, and optional CSI motion factor.
        Returns:
            (state_name, normalized_motion_score)
        """
        # Combine RSSI deviation with CSI motion factor if available
        # When CSI is available, it provides subcarrier sensitivity even for small deviations
        effective_metric = deviation + (csi_motion_factor * 5.0)

        # Normalized motion score between 0.0 and 1.0
        motion_score = min(max(effective_metric / (self.movement_threshold * 1.5), 0.0), 1.0)

        if effective_metric < self.stable_threshold and variance < 1.0:
            status = "STABLE"
        elif effective_metric < self.low_activity_threshold:
            status = "LOW ACTIVITY"
        elif effective_metric < self.movement_threshold:
            status = "MOVEMENT"
        else:
            status = "HIGH ACTIVITY"

        return status, round(motion_score, 3)

    def calibrate_thresholds(self, baseline_variance: float, noise_floor: float):
        """Dynamically tunes classification boundaries based on measured environmental noise floor."""
        noise_margin = max(noise_floor, 0.5)
        self.stable_threshold = round(1.5 * noise_margin + 0.5, 2)
        self.low_activity_threshold = round(self.stable_threshold + 2.0, 2)
        self.movement_threshold = round(self.low_activity_threshold + 3.0, 2)
