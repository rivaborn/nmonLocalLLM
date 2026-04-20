import pytest
from unittest.mock import Mock
from src.nmon.widgets.sparkline import Sparkline, ThresholdLine

def test_sparkline_init():
    """Test Sparkline initialization with basic parameters"""
    title = "Test Sparkline"
    series = [("Series 1", [1.0, 2.0, 3.0, 4.0, 5.0])]
    y_min = 0.0
    y_max = 10.0
    width = 100
    height = 50
    
    sparkline = Sparkline(
        title=title,
        series=series,
        y_min=y_min,
        y_max=y_max,
        width=width,
        height=height
    )
    
    assert sparkline.title == title
    assert sparkline.series == series
    assert sparkline.y_min == y_min
    assert sparkline.y_max == y_max
    assert sparkline.width == width
    assert sparkline.height == height

def test_sparkline_init_with_guide_lines():
    """Test Sparkline initialization with guide lines"""
    title = "Test Sparkline with Guide Lines"
    series = [("Series 1", [1.0, 2.0, 3.0, 4.0, 5.0])]
    y_min = 0.0
    y_max = 10.0
    width = 100
    height = 50
    guide_lines = [2.0, 5.0, 8.0]
    
    sparkline = Sparkline(
        title=title,
        series=series,
        y_min=y_min,
        y_max=y_max,
        width=width,
        height=height,
        guide_lines=guide_lines
    )
    
    assert sparkline.guide_lines == guide_lines

def test_sparkline_init_with_threshold():
    """Test Sparkline initialization with threshold line"""
    title = "Test Sparkline with Threshold"
    series = [("Series 1", [1.0, 2.0, 3.0, 4.0, 5.0])]
    y_min = 0.0
    y_max = 10.0
    width = 100
    height = 50
    threshold = ThresholdLine(value=3.0, color="red")
    
    sparkline = Sparkline(
        title=title,
        series=series,
        y_min=y_min,
        y_max=y_max,
        width=width,
        height=height,
        threshold=threshold
    )
    
    assert sparkline.threshold == threshold

def test_sparkline_init_empty_series():
    """Test Sparkline initialization with empty series"""
    title = "Test Sparkline Empty Series"
    series = []
    y_min = 0.0
    y_max = 10.0
    width = 100
    height = 50
    
    sparkline = Sparkline(
        title=title,
        series=series,
        y_min=y_min,
        y_max=y_max,
        width=width,
        height=height
    )
    
    assert sparkline.series == series

def test_sparkline_init_multiple_series():
    """Test Sparkline initialization with multiple series"""
    title = "Test Sparkline Multiple Series"
    series = [
        ("Series 1", [1.0, 2.0, 3.0]),
        ("Series 2", [4.0, 5.0, 6.0]),
        ("Series 3", [7.0, 8.0, 9.0])
    ]
    y_min = 0.0
    y_max = 10.0
    width = 100
    height = 50
    
    sparkline = Sparkline(
        title=title,
        series=series,
        y_min=y_min,
        y_max=y_max,
        width=width,
        height=height
    )
    
    assert sparkline.series == series
