"""
Tests for the analyzer module.
"""

import pytest
from apppermission_analyzer import Analyzer


def test_analyzer_initialization():
    """Test that analyzer can be initialized."""
    analyzer = Analyzer()
    assert analyzer is not None


def test_permission_categorization():
    """Test permission categorization."""
    analyzer = Analyzer()
    assert analyzer._categorize_permission("android.permission.ACCESS_FINE_LOCATION") == "Location"
    assert analyzer._categorize_permission("android.permission.CAMERA") == "Camera"
    assert analyzer._categorize_permission("android.permission.INTERNET") == "Network"


def test_risk_assessment():
    """Test risk assessment."""
    analyzer = Analyzer()
    assert analyzer._assess_risk("android.permission.ACCESS_FINE_LOCATION") == "high"
    assert analyzer._assess_risk("android.permission.INTERNET") == "medium"
    assert analyzer._assess_risk("android.permission.VIBRATE") == "low"



