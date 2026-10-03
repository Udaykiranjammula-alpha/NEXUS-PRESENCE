"""
RF Signal Feature Extraction
Author: Uday Kiran Jammula
"""

import math
from typing import List, Dict
import numpy as np

class FeatureExtractor:
    """Extracts statistical, temporal, and frequency-domain features from RF signal windows."""

    @staticmethod
    def extract_features(signal_window: List[float]) -> Dict[str, float]:
        if not signal_window or len(signal_window) < 2:
            return {
                "mean": 0.0,
                "std": 0.0,
                "skewness": 0.0,
                "kurtosis": 0.0,
                "energy": 0.0,
                "peak_to_peak": 0.0,
                "rate_of_change": 0.0
            }

        arr = np.array(signal_window, dtype=np.float64)
        n = len(arr)
        mean_val = float(np.mean(arr))
        std_val = float(np.std(arr))
        
        # Peak-to-peak swing
        p2p = float(np.max(arr) - np.min(arr))

        # Normalized centered moments
        diff = arr - mean_val
        if std_val > 1e-6:
            skew = float(np.mean(diff ** 3) / (std_val ** 3))
            kurt = float(np.mean(diff ** 4) / (std_val ** 4) - 3.0)  # Excess kurtosis
        else:
            skew = 0.0
            kurt = 0.0

        # Signal Energy
        energy = float(np.sum(diff ** 2) / n)

        # Average Absolute First Difference (Rate of change)
        roc = float(np.mean(np.abs(np.diff(arr))))

        return {
            "mean": round(mean_val, 2),
            "std": round(std_val, 3),
            "skewness": round(skew, 3),
            "kurtosis": round(kurt, 3),
            "energy": round(energy, 3),
            "peak_to_peak": round(p2p, 2),
            "rate_of_change": round(roc, 3)
        }
