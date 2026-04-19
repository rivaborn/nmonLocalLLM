import pytest
from unittest.mock import patch, MagicMock
from nmon.ui.alert_bar import AlertBar
from nmon.llm.protocol import LlmSample


def test_alert_bar_shows_orange_for_low_utilization():
    """Test that AlertBar shows orange color when gpu_utilization_pct <= 5%."""
    # Create an AlertBar instance
    alert_bar = AlertBar()
    
    # Create a sample with low GPU utilization (3%)
    sample = LlmSample(
        timestamp=1.0,
        model_name="test",
        model_size_bytes=1000,
        gpu_utilization_pct=3.0,
        cpu_utilization_pct=97.0,
        gpu_layers_offloaded=1,
        total_layers=32
    )
    
    # Call update_alert with the sample
    alert_bar.update_alert(sample)
    
    # Assert that the alert bar is visible
    assert alert_bar.visible is True
    
    # Assert that the color is orange (#FF8C00)
    assert alert_bar.styles.color == "#FF8C00"
    
    # Assert that the message contains the expected text
    assert "⚠ GPU OFFLOADING ACTIVE" in alert_bar.renderable


def test_alert_bar_shows_red_for_high_utilization():
    """Test that AlertBar shows red color when gpu_utilization_pct > 5%."""
    # Create an AlertBar instance
    alert_bar = AlertBar()
    
    # Create a sample with high GPU utilization (10%)
    sample = LlmSample(
        timestamp=1.0,
        model_name="test",
        model_size_bytes=1000,
        gpu_utilization_pct=10.0,
        cpu_utilization_pct=90.0,
        gpu_layers_offloaded=3,
        total_layers=32
    )
    
    # Call update_alert with the sample
    alert_bar.update_alert(sample)
    
    # Assert that the alert bar is visible
    assert alert_bar.visible is True
    
    # Assert that the color is red (#FF0000)
    assert alert_bar.styles.color == "#FF0000"
    
    # Assert that the message contains the expected text
    assert "⚠ GPU OFFLOADING ACTIVE" in alert_bar.renderable


def test_alert_bar_hidden_for_full_utilization():
    """Test that AlertBar is hidden when gpu_utilization_pct == 100%."""
    # Create an AlertBar instance
    alert_bar = AlertBar()
    
    # Create a sample with full GPU utilization (100%)
    sample = LlmSample(
        timestamp=1.0,
        model_name="test",
        model_size_bytes=1000,
        gpu_utilization_pct=100.0,
        cpu_utilization_pct=0.0,
        gpu_layers_offloaded=32,
        total_layers=32
    )
    
    # Call update_alert with the sample
    alert_bar.update_alert(sample)
    
    # Assert that the alert bar is not visible
    assert alert_bar.visible is False


def test_alert_bar_message_format():
    """Test that AlertBar displays correct message format with offload percentage."""
    # Create an AlertBar instance
    alert_bar = AlertBar()
    
    # Create a sample with 20% GPU utilization (80% offloaded)
    sample = LlmSample(
        timestamp=1.0,
        model_name="test",
        model_size_bytes=1000,
        gpu_utilization_pct=20.0,
        cpu_utilization_pct=80.0,
        gpu_layers_offloaded=6,
        total_layers=32
    )
    
    # Call update_alert with the sample
    alert_bar.update_alert(sample)
    
    # Assert that the message is formatted correctly
    # Expected message: "⚠ GPU OFFLOADING ACTIVE — 80.0% on CPU"
    assert "⚠ GPU OFFLOADING ACTIVE — 80.0% on CPU" in alert_bar.renderable


def test_alert_bar_minimum_visibility_duration():
    """Test that AlertBar remains visible for minimum 1000 ms after appearing."""
    # Mock time.time to control time progression
    with patch('time.time') as mock_time:
        # Set initial time
        mock_time.return_value = 1.0
        
        # Create an AlertBar instance
        alert_bar = AlertBar()
        
        # Create a sample
        sample = LlmSample(
            timestamp=1.0,
            model_name="test",
            model_size_bytes=1000,
            gpu_utilization_pct=10.0,
            cpu_utilization_pct=90.0,
            gpu_layers_offloaded=3,
            total_layers=32
        )
        
        # Call update_alert with the sample
        alert_bar.update_alert(sample)
        
        # Assert that the alert bar is visible
        assert alert_bar.visible is True
        
        # Advance time by 1000 ms (1 second)
        mock_time.return_value = 2.0
        
        # Simulate timer completion
        alert_bar._on_timer()
        
        # Assert that the alert bar is no longer visible after timer completion
        assert alert_bar.visible is False


def test_alert_bar_timer_reset_on_new_sample():
    """Test that AlertBar timer resets on new sample with different utilization."""
    # Mock time.time to control time progression
    with patch('time.time') as mock_time:
        # Set initial time
        mock_time.return_value = 1.0
        
        # Create an AlertBar instance
        alert_bar = AlertBar()
        
        # Create a sample with 10% GPU utilization
        sample1 = LlmSample(
            timestamp=1.0,
            model_name="test",
            model_size_bytes=1000,
            gpu_utilization_pct=10.0,
            cpu_utilization_pct=90.0,
            gpu_layers_offloaded=3,
            total_layers=32
        )
        
        # Create a sample with 20% GPU utilization
        sample2 = LlmSample(
            timestamp=2.0,
            model_name="test",
            model_size_bytes=1000,
            gpu_utilization_pct=20.0,
            cpu_utilization_pct=80.0,
            gpu_layers_offloaded=6,
            total_layers=32
        )
        
        # Call update_alert with the first sample
        alert_bar.update_alert(sample1)
        
        # Assert that the alert bar is visible
        assert alert_bar.visible is True
        
        # Advance time by 500 ms
        mock_time.return_value = 1.5
        
        # Call update_alert with the second sample (should reset timer)
        alert_bar.update_alert(sample2)
        
        # Assert that the timer was reset and the bar remains visible
        assert alert_bar.visible is True


def test_alert_bar_handles_none_sample():
    """Test that AlertBar handles None sample gracefully."""
    # Create an AlertBar instance
    alert_bar = AlertBar()
    
    # Call update_alert with None
    alert_bar.update_alert(None)
    
    # Assert that the alert bar is not visible
    assert alert_bar.visible is False


def test_alert_bar_handles_invalid_sample():
    """Test that AlertBar handles invalid sample gracefully."""
    # Create an AlertBar instance
    alert_bar = AlertBar()
    
    # Create a sample with invalid gpu_utilization_pct
    sample = LlmSample(
        timestamp=1.0,
        model_name="test",
        model_size_bytes=1000,
        gpu_utilization_pct=150.0,  # Invalid value
        cpu_utilization_pct=0.0,
        gpu_layers_offloaded=32,
        total_layers=32
    )
    
    # Call update_alert with the invalid sample
    alert_bar.update_alert(sample)
    
    # Assert that the alert bar is not visible
    assert alert_bar.visible is False
