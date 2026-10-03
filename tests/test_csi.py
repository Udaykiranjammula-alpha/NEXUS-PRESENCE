"""
Unit Tests for CSI Processing and Subcarrier Metrics
Author: Uday Kiran Jammula
"""

import pytest
from backend.processing.csi_processor import CSIProcessor

def test_csi_empty_handling():
    proc = CSIProcessor(node_id=2)
    # When no CSI hardware is present
    res = proc.process(amplitudes=[])
    assert res["csi_supported"] is False
    assert res["subcarrier_count"] == 0
    assert res["amplitude_mean"] == 0.0

def test_csi_valid_subcarrier_metrics():
    proc = CSIProcessor(node_id=2)
    # HT20 typical 52 subcarrier amplitudes
    amplitudes = [10 + (i % 5) for i in range(52)]
    res = proc.process(amplitudes=amplitudes)
    assert res["csi_supported"] is True
    assert res["subcarrier_count"] == 52
    assert res["amplitude_mean"] > 0
    assert res["subcarrier_variance"] > 0
    assert "high_frequency_energy" in res

def test_csi_motion_factor_detection():
    proc = CSIProcessor(node_id=2)
    # Initial steady packets
    for _ in range(6):
        proc.process(amplitudes=[15] * 32)
    
    # Sudden disturbed packet
    disturbed = [15 + (i * 2) for i in range(32)]
    res = proc.process(amplitudes=disturbed)
    assert res["csi_motion_factor"] > 0.0
