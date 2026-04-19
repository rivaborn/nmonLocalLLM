import pytest
from unittest.mock import MagicMock, patch
from nmon.ui.llm_tab import LlmTab
from nmon.llm.protocol import LlmSample
from nmon.config import AppConfig
from nmon.storage.ring_buffer import RingBuffer
import time

@pytest.fixture
def mock_app_config():
    config = MagicMock(spec=AppConfig)
    config.poll_interval_s = 1.0
    config.history_duration_s = 60.0
    return config

@pytest.fixture
def mock_llm_monitor():
    return MagicMock()

@pytest.fixture
def llm_tab(mock_app_config, mock_llm_monitor):
    return LlmTab(mock_app_config, mock_llm_monitor)

def test_llm_tab_initialization(mock_app_config, mock_llm_monitor):
    """Test that LlmTab initializes correctly"""
    tab = LlmTab(mock_app_config, mock_llm_monitor)
    
    assert tab.config == mock_app_config
    assert tab.llm_monitor == mock_llm_monitor
    assert hasattr(tab, 'ring_buffer')
    assert hasattr(tab, 'llm_samples')

def test_llm_tab_update_samples(mock_app_config, mock_llm_monitor):
    """Test that LlmTab updates samples correctly"""
    tab = LlmTab(mock_app_config, mock_llm_monitor)
    
    # Mock sample data
    sample1 = LlmSample(
        timestamp=time.time(),
        prompt_tokens=100,
        completion_tokens=200,
        total_tokens=300,
        prompt_time_s=0.1,
        completion_time_s=0.2,
        total_time_s=0.3
    )
    
    sample2 = LlmSample(
        timestamp=time.time() + 1,
        prompt_tokens=150,
        completion_tokens=250,
        total_tokens=400,
        prompt_time_s=0.15,
        completion_time_s=0.25,
        total_time_s=0.4
    )
    
    # Mock the monitor's get_samples method
    mock_llm_monitor.get_samples.return_value = [sample1, sample2]
    
    # Update samples
    tab.update_samples()
    
    # Verify samples were added to ring buffer
    assert len(tab.ring_buffer) == 2
    assert tab.ring_buffer[0] == sample1
    assert tab.ring_buffer[1] == sample2

def test_llm_tab_update_samples_empty(mock_app_config, mock_llm_monitor):
    """Test that LlmTab handles empty samples correctly"""
    tab = LlmTab(mock_app_config, mock_llm_monitor)
    
    # Mock empty samples
    mock_llm_monitor.get_samples.return_value = []
    
    # Update samples
    tab.update_samples()
    
    # Verify ring buffer is empty
    assert len(tab.ring_buffer) == 0

def test_llm_tab_update_samples_with_filtering(mock_app_config, mock_llm_monitor):
    """Test that LlmTab filters samples based on timestamp"""
    tab = LlmTab(mock_app_config, mock_llm_monitor)
    
    # Set up a timestamp that should filter out old samples
    current_time = time.time()
    old_sample = LlmSample(
        timestamp=current_time - 100,  # 100 seconds old
        prompt_tokens=100,
        completion_tokens=200,
        total_tokens=300,
        prompt_time_s=0.1,
        completion_time_s=0.2,
        total_time_s=0.3
    )
    
    new_sample = LlmSample(
        timestamp=current_time,
        prompt_tokens=150,
        completion_tokens=250,
        total_tokens=400,
        prompt_time_s=0.15,
        completion_time_s=0.25,
        total_time_s=0.4
    )
    
    mock_llm_monitor.get_samples.return_value = [old_sample, new_sample]
    
    # Update samples
    tab.update_samples()
    
    # Only new sample should be in ring buffer (old one filtered out)
    assert len(tab.ring_buffer) == 1
    assert tab.ring_buffer[0] == new_sample

def test_llm_tab_get_stats(mock_app_config, mock_llm_monitor):
    """Test that LlmTab calculates statistics correctly"""
    tab = LlmTab(mock_app_config, mock_llm_monitor)
    
    # Add some sample data
    sample1 = LlmSample(
        timestamp=time.time(),
        prompt_tokens=100,
        completion_tokens=200,
        total_tokens=300,
        prompt_time_s=0.1,
        completion_time_s=0.2,
        total_time_s=0.3
    )
    
    sample2 = LlmSample(
        timestamp=time.time() + 1,
        prompt_tokens=150,
        completion_tokens=250,
        total_tokens=400,
        prompt_time_s=0.15,
        completion_time_s=0.25,
        total_time_s=0.4
    )
    
    tab.ring_buffer = MagicMock()
    tab.ring_buffer.__len__.return_value = 2
    tab.ring_buffer.__getitem__.side_effect = [sample1, sample2]
    
    # Get stats
    stats = tab.get_stats()
    
    # Verify stats are calculated
    assert 'prompt_tokens' in stats
    assert 'completion_tokens' in stats
    assert 'total_tokens' in stats
    assert 'prompt_time_s' in stats
    assert 'completion_time_s' in stats
    assert 'total_time_s' in stats

def test_llm_tab_get_stats_empty(mock_app_config, mock_llm_monitor):
    """Test that LlmTab handles empty stats correctly"""
    tab = LlmTab(mock_app_config, mock_llm_monitor)
    
    # Empty ring buffer
    tab.ring_buffer = MagicMock()
    tab.ring_buffer.__len__.return_value = 0
    
    # Get stats
    stats = tab.get_stats()
    
    # Verify empty stats
    assert stats == {}
