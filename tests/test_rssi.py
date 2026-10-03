"""
Unit Tests for RSSI Processing, Noise Filtering, and Baseline Estimation
Author: Uday Kiran Jammula
"""

import pytest
from backend.processing.noise_filter import ExponentialFilter, MedianFilter, OutlierRejector
from backend.processing.rssi_processor import RSSIProcessor
from backend.processing.feature_extraction import FeatureExtractor

def test_exponential_filter():
    flt = ExponentialFilter(alpha=0.5)
    # First measurement initializes state
    v1 = flt.update(-50.0)
    assert v1 == -50.0
    # Second measurement applies EMA: 0.5 * (-40) + 0.5 * (-50) = -45
    v2 = flt.update(-40.0)
    assert pytest.approx(v2, 0.01) == -45.0

def test_median_filter_spike_suppression():
    flt = MedianFilter(window_size=5)
    # Feed regular series with an outlier spike
    readings = [-50.0, -51.0, -10.0, -50.0, -49.0]
    out = None
    for r in readings:
        out = flt.update(r)
    # The middle sorted value should be around -50, ignoring the spike of -10
    assert out == -50.0

def test_rssi_processor_baseline_and_deviation():
    proc = RSSIProcessor(node_id=2, window_size=10)
    
    # Empty room calibration with stable signal
    calibration_samples = [-50.0] * 15
    proc.calibrate(calibration_samples)
    assert proc.calibrated is True
    assert pytest.approx(proc.baseline, 0.1) == -50.0

    # Test perturbation deviation
    filt, avg, dev, var = proc.process(-60.0)
    assert dev > 0.0
    assert filt < -50.0

def test_feature_extraction():
    signals = [-50.0, -52.0, -48.0, -51.0, -49.0]
    features = FeatureExtractor.extract_features(signals)
    assert "mean" in features
    assert "std" in features
    assert "energy" in features
    assert features["peak_to_peak"] == 4.0
