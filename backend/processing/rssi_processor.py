"""
RSSI Signal Processor
Author: Uday Kiran Jammula
"""

import collections
import math
from typing import List, Tuple, Optional
from backend.processing.noise_filter import ExponentialFilter, MedianFilter

class RSSIProcessor:
    """
    Stateful processor for a single ESP32 node's RSSI telemetry stream.
    Applies noise suppression, rolling window statistics, baseline tracking,
    and deviation calculations.
    """
    def __init__(self, node_id: int, window_size: int = 10, baseline_alpha: float = 0.005):
        self.node_id = node_id
        self.window_size = window_size
        self.baseline_alpha = baseline_alpha
        
        self.raw_history = collections.deque(maxlen=window_size)
        self.median_filter = MedianFilter(window_size=5)
        self.ema_filter = ExponentialFilter(alpha=0.35)
        
        self.baseline: Optional[float] = None
        self.baseline_variance: float = 0.0
        self.calibrated: bool = False
        self.total_samples: int = 0

    def calibrate(self, initial_samples: List[float]):
        """Calibrates empty-room baseline from a list of clean samples."""
        if not initial_samples:
            return
        self.baseline = float(sum(initial_samples) / len(initial_samples))
        sq_diff = [(x - self.baseline) ** 2 for x in initial_samples]
        self.baseline_variance = float(sum(sq_diff) / len(initial_samples))
        self.calibrated = True

    def process(self, raw_rssi: float) -> Tuple[float, float, float, float]:
        """
        Ingests a new raw RSSI reading.
        Returns:
            (filtered_rssi, moving_average, deviation_from_baseline, variance)
        """
        self.total_samples += 1
        
        # 1. Median filter spike suppression
        med_rssi = self.median_filter.update(raw_rssi)
        
        # 2. Exponential Moving Average
        filtered_rssi = self.ema_filter.update(med_rssi)
        
        # 3. Update circular buffer
        self.raw_history.append(filtered_rssi)
        
        # 4. Compute moving average & variance
        n = len(self.raw_history)
        avg_rssi = sum(self.raw_history) / n
        variance = sum((x - avg_rssi) ** 2 for x in self.raw_history) / n if n > 1 else 0.0
        
        # 5. Initialize or adapt baseline
        if self.baseline is None:
            self.baseline = avg_rssi
        elif not self.calibrated and self.total_samples > 20:
            self.calibrated = True
        elif self.calibrated and variance < 0.5:
            # Slow adaptation to diurnal RF environment changes only when state is highly stable
            self.baseline = (1.0 - self.baseline_alpha) * self.baseline + self.baseline_alpha * avg_rssi

        # 6. Deviation from baseline
        deviation = abs(avg_rssi - self.baseline)
        
        return filtered_rssi, avg_rssi, deviation, variance
