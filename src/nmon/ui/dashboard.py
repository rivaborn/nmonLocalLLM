from typing import List, Optional
from nicegui import ui
from nmon.gpu.protocol import GpuSample
from nmon.llm.protocol import LlmSample
from nmon.config import AppConfig
from nmon.storage.ring_buffer import RingBuffer
from nmon.gpu.protocol import GpuMonitorProtocol
from nmon.llm.protocol import LlmMonitorProtocol
from nicegui.elements.vertical import Vertical


class DashboardTab(Vertical):
    def __init__(self, config: AppConfig, gpu_buffer: RingBuffer[GpuSample],
                 llm_buffer: RingBuffer[LlmSample], gpu_monitor: GpuMonitorProtocol,
                 llm_monitor: LlmMonitorProtocol):
        self.config = config
        self.gpu_buffer = gpu_buffer
        self.llm_buffer = llm_buffer
        self.gpu_monitor = gpu_monitor
        self.llm_monitor = llm_monitor
        
        self.gpu_sections: List[ui.element] = []
        self.llm_section: Optional[ui.element] = None
        
        super().__init__(id='dashboard-tab', classes='q-pa-md')
        
        # Build initial content
        self._build_initial_content()
    
    def _build_initial_content(self):
        """Build initial content for the dashboard"""
        with self:
            # GPU sections will be added here
            self.gpu_container = ui.column().classes('q-gutter-md')
            
            # LLM section if monitor is present
            if self.llm_monitor:
                self.llm_container = ui.column().classes('q-gutter-md')
    
    async def _build_gpu_sections(self) -> None:
        """Build GPU sections with current data"""
        # Get current GPU samples
        samples = self.gpu_buffer.get_all()
        
        # Clear existing sections
        for section in self.gpu_sections:
            section.delete()
        self.gpu_sections.clear()
        
        if not samples:
            # Add a message if no samples available
            with self.gpu_container:
                ui.label("No GPU data available").classes('text-center text-grey')
            return
        
        # Get unique GPU indices from samples
        gpu_indices = set()
        for sample in samples:
            gpu_indices.add(sample.gpu_index)
        
        # Build sections for each GPU
        for gpu_index in sorted(gpu_indices):
            # Get latest sample for this GPU
            latest_sample = None
            for sample in reversed(samples):
                if sample.gpu_index == gpu_index:
                    latest_sample = sample
                    break
            
            if latest_sample is None:
                continue
            
            # Compute 24h max and 1h avg temperatures
            temp_24h_max = latest_sample.temperature_c
            temp_1h_avg = latest_sample.temperature_c
            
            # Compute memory usage percentage
            if latest_sample.memory_total_mb > 0:
                memory_percent = (latest_sample.memory_used_mb / latest_sample.memory_total_mb) * 100
            else:
                memory_percent = 0
            
            # Compute power draw percentage
            if latest_sample.power_limit_w > 0:
                power_percent = (latest_sample.power_draw_w / latest_sample.power_limit_w) * 100
            else:
                power_percent = 0
            
            # Create GPU section widget
            with self.gpu_container:
                gpu_section = ui.card().classes('q-pa-md')
                with gpu_section:
                    ui.label(f"GPU {gpu_index}").classes('text-h6')
                    ui.row().classes('q-gutter-md').bind(
                        lambda temp_24h_max=temp_24h_max, temp_1h_avg=temp_1h_avg, 
                              memory_percent=memory_percent, power_percent=power_percent: [
                            ui.label(f"Temp: {temp_24h_max}°C (max 24h)"),
                            ui.label(f"Temp: {temp_1h_avg}°C (avg 1h)"),
                            ui.label(f"Memory: {memory_percent:.1f}%"),
                            ui.label(f"Power: {power_percent:.1f}%")
                        ]
                    )
                
                self.gpu_sections.append(gpu_section)
    
    async def _build_llm_section(self) -> None:
        """Build LLM section with current data"""
        # Get latest LLM sample
        latest_sample = self.llm_buffer.get_latest()
        
        if latest_sample is None:
            return
        
        # Compute GPU and CPU utilization percentages
        gpu_util = latest_sample.gpu_utilization_percent
        cpu_util = latest_sample.cpu_utilization_percent
        
        # Compute offloaded layers ratio
        if latest_sample.total_layers > 0:
            offloaded_ratio = latest_sample.offloaded_layers / latest_sample.total_layers
        else:
            offloaded_ratio = 0
        
        # Create LLM section widget
        with self.llm_container:
            self.llm_section = ui.card().classes('q-pa-md')
            with self.llm_section:
                ui.label("LLM Server").classes('text-h6')
                ui.row().classes('q-gutter-md').bind(
                    lambda gpu_util=gpu_util, cpu_util=cpu_util, 
                          offloaded_ratio=offloaded_ratio: [
                        ui.label(f"GPU Util: {gpu_util:.1f}%"),
                        ui.label(f"CPU Util: {cpu_util:.1f}%"),
                        ui.label(f"Offloaded: {offloaded_ratio:.1f}")
                    ]
                )
    
    async def _update_display(self) -> None:
        """Update the display with fresh data"""
        try:
            # Rebuild GPU sections with fresh data
            await self._build_gpu_sections()
            
            # Rebuild LLM section if present
            if self.llm_monitor:
                await self._build_llm_section()
                
        except Exception as e:
            # Handle any exceptions during update gracefully
            print(f"Error updating dashboard: {e}")
            # Optionally show an error message in UI
            # ui.notify(f"Error updating dashboard: {e}", type='negative')
