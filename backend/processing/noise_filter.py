"""
Noise Filtering & Signal Conditioning
Author: Uday Kiran Jammula
"""

import collections
from typing import List, Optional
import numpy as np

class ExponentialFilter:
    """Exponential Moving Average (EMA) filter for smoothing high-frequency RF jitter."""
    def __init__(self, alpha: float = 0.35):
        if not (0.0 < alpha <= 1.0):
            raise ValueError("Alpha must be in range (0.0, 1.0]")
        self.alpha = alpha
        self.state: Optional[float] = None

    def update(self, measurement: float) -> float:
        if self.state is None:
            self.state = measurement
        else:
            self.state = self.alpha * measurement + (1.0 - self.alpha) * self.state
        return self.state

    def reset(self):
        self.state = None


class MedianFilter:
    """Sliding-window median filter for non-linear pulse/spike suppression."""
    def __init__(self, window_size: int = 5):
        if window_size % 2 == 0:
            window_size += 1  # enforce odd window size for clear median
        self.window_size = window_size
        self.buffer = collections.deque(maxlen=window_size)

    def update(self, measurement: float) -> float:
        self.buffer.append(measurement)
        sorted_window = sorted(self.buffer)
        mid_idx = len(sorted_window) // 2
        return sorted_window[mid_idx]


class OutlierRejector:
    """Hampel-inspired threshold rejector using rolling MAD (Median Absolute Deviation)."""
    def __init__(self, max_deviation_db: float = 12.0):
        self.max_deviation_db = max_deviation_db
        self.last_valid: Optional[float] = None

    def filter(self, measurement: float, baseline: float) -> float:
        if self.last_valid is None:
            self.last_valid = measurement
            return measurement

        # If a single frame deviates drastically beyond physics of human movement in RF
        if abs(measurement - baseline) > self.max_deviation_db:
            # Dampen spike towards previous valid measurement
            clamped = self.last_valid * 0.8 + baseline * 0.2
            return clamped
        
        self.last_valid = measurement
        return measurement
