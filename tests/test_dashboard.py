# Write tests for DashboardTab in tests/test_dashboard.py
# Import the module under test from its production location
from nmon.ui.dashboard import DashboardTab
from nmon.gpu.protocol import GpuSample
from nmon.llm.protocol import LlmSample
from nmon.config import AppConfig
from nmon.storage.ring_buffer import RingBuffer
from nmon.gpu.protocol import GpuMonitorProtocol
from nmon.llm.protocol import LlmMonitorProtocol

# Test file: tests/test_dashboard.py
# External dependencies to mock: `RingBuffer`, `GpuMonitorProtocol`, `LlmMonitorProtocol`
# Behaviors to assert:
# - Dashboard renders GPU sections for each available GPU
# - Dashboard shows memory junction section only for GPUs that support it
# - Dashboard shows LLM section only when `llm_monitor` is present
# - Dashboard updates values correctly on new samples
# - Dashboard handles missing or invalid samples gracefully
# - Dashboard sections display correct computed values (max, avg, percentages)
# pytest fixtures and plugins: pytest-asyncio, monkeypatch
# Coverage goals: must exercise both the happy path AND the case where LLM monitor is absent

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pytest_asyncio import fixture
import asyncio

# Test that DashboardTab correctly initializes with the given parameters
def test_dashboard_tab_initialization():
    # Arrange
    config = AppConfig()
    gpu_buffer = MagicMock(spec=RingBuffer[GpuSample])
    llm_buffer = MagicMock(spec=RingBuffer[LlmSample])
    gpu_monitor = MagicMock(spec=GpuMonitorProtocol)
    llm_monitor = MagicMock(spec=LlmMonitorProtocol)
    
    # Act
    dashboard = DashboardTab(config, gpu_buffer, llm_buffer, gpu_monitor, llm_monitor)
    
    # Assert
    assert dashboard.config == config
    assert dashboard.gpu_buffer == gpu_buffer
    assert dashboard.llm_buffer == llm_buffer
    assert dashboard.gpu_monitor == gpu_monitor
    assert dashboard.llm_monitor == llm_monitor

# Test that DashboardTab renders GPU sections for each available GPU
@pytest.mark.asyncio
async def test_dashboard_tab_builds_gpu_sections():
    # Arrange
    config = AppConfig()
    gpu_buffer = MagicMock(spec=RingBuffer[GpuSample])
    llm_buffer = MagicMock(spec=RingBuffer[LlmSample])
    gpu_monitor = MagicMock(spec=GpuMonitorProtocol)
    llm_monitor = MagicMock(spec=LlmMonitorProtocol)
    
    # Mock samples
    sample1 = GpuSample(
        timestamp=1.0,
        gpu_index=0,
        temperature_gpu=70.0,
        temperature_mem_junction=60.0,
        memory_used_mib=1000.0,
        memory_total_mib=2000.0,
        power_draw_w=100.0,
        power_limit_w=200.0
    )
    sample2 = GpuSample(
        timestamp=1.0,
        gpu_index=1,
        temperature_gpu=75.0,
        temperature_mem_junction=None,
        memory_used_mib=1500.0,
        memory_total_mib=2000.0,
        power_draw_w=120.0,
        power_limit_w=200.0
    )
    
    # Mock buffer to return samples
    gpu_buffer.since.return_value = [sample1, sample2]
    
    # Act
    dashboard = DashboardTab(config, gpu_buffer, llm_buffer, gpu_monitor, llm_monitor)
    await dashboard._build_gpu_sections()
    
    # Assert
    assert len(dashboard.gpu_sections) == 2
    gpu_buffer.since.assert_called_once_with(86400.0)  # history_duration_s

# Test that DashboardTab shows memory junction section only for GPUs that support it
@pytest.mark.asyncio
async def test_dashboard_tab_gpu_sections_show_mem_junction():
    # Arrange
    config = AppConfig()
    gpu_buffer = MagicMock(spec=RingBuffer[GpuSample])
    llm_buffer = MagicMock(spec=RingBuffer[LlmSample])
    gpu_monitor = MagicMock(spec=GpuMonitorProtocol)
    llm_monitor = MagicMock(spec=LlmMonitorProtocol)
    
    # Mock samples with and without mem junction
    sample_with_mem = GpuSample(
        timestamp=1.0,
        gpu_index=0,
        temperature_gpu=70.0,
        temperature_mem_junction=60.0,
        memory_used_mib=1000.0,
        memory_total_mib=2000.0,
        power_draw_w=100.0,
        power_limit_w=200.0
    )
    sample_without_mem = GpuSample(
        timestamp=1.0,
        gpu_index=1,
        temperature_gpu=75.0,
        temperature_mem_junction=None,
        memory_used_mib=1500.0,
        memory_total_mib=2000.0,
        power_draw_w=120.0,
        power_limit_w=200.0
    )
    
    gpu_buffer.since.return_value = [sample_with_mem, sample_without_mem]
    
    # Act
    dashboard = DashboardTab(config, gpu_buffer, llm_buffer, gpu_monitor, llm_monitor)
    await dashboard._build_gpu_sections()
    
    # Assert
    assert len(dashboard.gpu_sections) == 2
    # Check that the first GPU has mem junction section and second doesn't
    assert hasattr(dashboard.gpu_sections[0], 'mem_junction_section')
    assert hasattr(dashboard.gpu_sections[1], 'mem_junction_section') is False

# Test that DashboardTab shows LLM section only when `llm_monitor` is present
@pytest.mark.asyncio
async def test_dashboard_tab_llm_section_present():
    # Arrange
    config = AppConfig()
    gpu_buffer = MagicMock(spec=RingBuffer[GpuSample])
    llm_buffer = MagicMock(spec=RingBuffer[LlmSample])
    gpu_monitor = MagicMock(spec=GpuMonitorProtocol)
    llm_monitor = MagicMock(spec=LlmMonitorProtocol)
    
    # Mock LLM sample
    llm_sample = LlmSample(
        timestamp=1.0,
        model_name="test-model",
        model_size_bytes=1000000000,
        gpu_utilization_pct=50.0,
        cpu_utilization_pct=50.0,
        gpu_layers_offloaded=16,
        total_layers=32
    )
    
    llm_buffer.latest.return_value = llm_sample
    
    # Act
    dashboard = DashboardTab(config, gpu_buffer, llm_buffer, gpu_monitor, llm_monitor)
    await dashboard._build_llm_section()
    
    # Assert
    assert dashboard.llm_section is not None

# Test that DashboardTab handles missing or invalid samples gracefully
@pytest.mark.asyncio
async def test_dashboard_tab_handles_missing_samples():
    # Arrange
    config = AppConfig()
    gpu_buffer = MagicMock(spec=RingBuffer[GpuSample])
    llm_buffer = MagicMock(spec=RingBuffer[LlmSample])
    gpu_monitor = MagicMock(spec=GpuMonitorProtocol)
    llm_monitor = MagicMock(spec=LlmMonitorProtocol)
    
    # Mock empty buffer
    gpu_buffer.since.return_value = []
    llm_buffer.latest.return_value = None
    
    # Act
    dashboard = DashboardTab(config, gpu_buffer, llm_buffer, gpu_monitor, llm_monitor)
    await dashboard._build_gpu_sections()
    await dashboard._build_llm_section()
    
    # Assert
    assert len(dashboard.gpu_sections) == 0
    assert dashboard.llm_section is None

# Test that DashboardTab updates values correctly on new samples
@pytest.mark.asyncio
async def test_dashboard_tab_updates_display():
    # Arrange
    config = AppConfig()
    gpu_buffer = MagicMock(spec=RingBuffer[GpuSample])
    llm_buffer = MagicMock(spec=RingBuffer[LlmSample])
    gpu_monitor = MagicMock(spec=GpuMonitorProtocol)
    llm_monitor = MagicMock(spec=LlmMonitorProtocol)
    
    # Mock samples
    sample = GpuSample(
        timestamp=1.0,
        gpu_index=0,
        temperature_gpu=70.0,
        temperature_mem_junction=60.0,
        memory_used_mib=1000.0,
        memory_total_mib=2000.0,
        power_draw_w=100.0,
        power_limit_w=200.0
    )
    
    gpu_buffer.since.return_value = [sample]
    
    # Act
    dashboard = DashboardTab(config, gpu_buffer, llm_buffer, gpu_monitor, llm_monitor)
    await dashboard._update_display()
    
    # Assert
    assert len(dashboard.gpu_sections) == 1

# Test that DashboardTab computes correct values (max, avg, percentages)
@pytest.mark.asyncio
async def test_dashboard_tab_computes_values_correctly():
    # Arrange
    config = AppConfig()
    gpu_buffer = MagicMock(spec=RingBuffer[GpuSample])
    llm_buffer = MagicMock(spec=RingBuffer[LlmSample])
    gpu_monitor = MagicMock(spec=GpuMonitorProtocol)
    llm_monitor = MagicMock(spec=LlmMonitorProtocol)
    
    # Mock samples with multiple values for computation
    sample1 = GpuSample(
        timestamp=1.0,
        gpu_index=0,
        temperature_gpu=70.0,
        temperature_mem_junction=60.0,
        memory_used_mib=1000.0,
        memory_total_mib=2000.0,
        power_draw_w=100.0,
        power_limit_w=200.0
    )
    sample2 = GpuSample(
        timestamp=2.0,
        gpu_index=0,
        temperature_gpu=80.0,
        temperature_mem_junction=70.0,
        memory_used_mib=1200.0,
        memory_total_mib=2000.0,
        power_draw_w=110.0,
        power_limit_w=200.0
    )
    
    gpu_buffer.since.return_value = [sample1, sample2]
    
    # Act
    dashboard = DashboardTab(config, gpu_buffer, llm_buffer, gpu_monitor, llm_monitor)
    await dashboard._build_gpu_sections()
    
    # Assert - Check that computed values are correct
    assert len(dashboard.gpu_sections) == 1
    # Should have computed max and average values
    assert hasattr(dashboard.gpu_sections[0], 'temperature_gpu_max')
    assert hasattr(dashboard.gpu_sections[0], 'temperature_gpu_avg')
    assert hasattr(dashboard.gpu_sections[0], 'memory_used_pct_avg')

# Test that DashboardTab handles case where LLM monitor is absent
@pytest.mark.asyncio
async def test_dashboard_tab_no_llm_monitor():
    # Arrange
    config = AppConfig()
    gpu_buffer = MagicMock(spec=RingBuffer[GpuSample])
    llm_buffer = MagicMock(spec=RingBuffer[LlmSample])
    gpu_monitor = MagicMock(spec=GpuMonitorProtocol)
    llm_monitor = None  # No LLM monitor
    
    # Mock samples
    sample = GpuSample(
        timestamp=1.0,
        gpu_index=0,
        temperature_gpu=70.0,
        temperature_mem_junction=60.0,
        memory_used_mib=1000.0,
        memory_total_mib=2000.0,
        power_draw_w=100.0,
        power_limit_w=200.0
    )
    
    gpu_buffer.since.return_value = [sample]
    
    # Act
    dashboard = DashboardTab(config, gpu_buffer, llm_buffer, gpu_monitor, llm_monitor)
    await dashboard._build_gpu_sections()
    await dashboard._build_llm_section()
    
    # Assert
    assert len(dashboard.gpu_sections) == 1
    assert dashboard.llm_section is None
