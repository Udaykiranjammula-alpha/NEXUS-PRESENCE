"""
CSI (Channel State Information) Signal Processor
Author: Uday Kiran Jammula
"""

import math
from typing import List, Dict, Optional, Tuple
import numpy as np

class CSIProcessor:
    """
    Analyzes fine-grained orthogonal frequency-division multiplexing (OFDM)
    subcarrier amplitudes and phases when reported by CSI-capable hardware.
    Gracefully handles empty/unsupported states.
    """
    def __init__(self, node_id: int):
        self.node_id = node_id
        self.is_supported = False
        self.total_packets_processed = 0
        self.subcarrier_baseline: Optional[np.ndarray] = None

    def process(
        self,
        amplitudes: Optional[List[int]],
        phases: Optional[List[int]] = None
    ) -> Dict[str, float]:
        """
        Processes subcarrier amplitudes and phases.
        Returns extracted metrics:
            - csi_supported: bool
            - subcarrier_count: int
            - amplitude_mean: float
            - subcarrier_variance: float
            - high_frequency_energy: float
            - phase_spread: float
        """
        if not amplitudes or len(amplitudes) == 0:
            return {
                "csi_supported": False,
                "subcarrier_count": 0,
                "amplitude_mean": 0.0,
                "subcarrier_variance": 0.0,
                "high_frequency_energy": 0.0,
                "phase_spread": 0.0,
                "csi_motion_factor": 0.0
            }

        self.is_supported = True
        self.total_packets_processed += 1
        
        amp_array = np.array(amplitudes, dtype=np.float64)
        count = len(amp_array)

        # Basic statistical properties across subcarriers
        amp_mean = float(np.mean(amp_array))
        subcarrier_variance = float(np.var(amp_array))

        # First-order difference across adjacent subcarriers (high-frequency ripple caused by multipath scattering)
        if count > 2:
            diffs = np.diff(amp_array)
            hf_energy = float(np.sum(diffs ** 2) / (count - 1))
        else:
            hf_energy = 0.0

        # Phase spread analysis if available
        phase_spread = 0.0
        if phases and len(phases) == count:
            phase_array = np.array(phases, dtype=np.float64)
            phase_spread = float(np.std(phase_array))

        # Baseline comparison
        if self.subcarrier_baseline is None and self.total_packets_processed > 5:
            self.subcarrier_baseline = amp_array.copy()

        csi_motion_factor = 0.0
        if self.subcarrier_baseline is not None and len(self.subcarrier_baseline) == count:
            delta = np.abs(amp_array - self.subcarrier_baseline)
            csi_motion_factor = float(np.mean(delta) / (amp_mean + 1e-5))

        return {
            "csi_supported": True,
            "subcarrier_count": count,
            "amplitude_mean": round(amp_mean, 2),
            "subcarrier_variance": round(subcarrier_variance, 3),
            "high_frequency_energy": round(hf_energy, 3),
            "phase_spread": round(phase_spread, 3),
            "csi_motion_factor": round(min(csi_motion_factor, 1.0), 3)
        }
