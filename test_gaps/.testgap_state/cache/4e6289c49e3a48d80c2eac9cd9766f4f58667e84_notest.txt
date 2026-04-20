# src/nmon/widgets/__init__.py

## Overall
NONE — no dedicated test file exists for this module.

## Must Test (Highest Risk First)
1. [LOW] `__init__.py`: Verify package import works correctly and exposes expected widgets
2. [LOW] Widget registration: Ensure all widget classes are properly registered in the package
3. [LOW] Widget factory functions: Test creation of widgets with different configurations
4. [LOW] Widget configuration loading: Verify widget settings are loaded from config
5. [LOW] Widget rendering methods: Test basic rendering behavior of widgets
6. [LOW] Widget update methods: Verify widget data update logic
7. [LOW] Widget layout handling: Test widget positioning and sizing
8. [LOW] Widget event handling: Verify widget responds to user input correctly
9. [LOW] Widget persistence: Test widget state saving and loading
10. [LOW] Widget error handling: Verify widget gracefully handles invalid data

## Mock Strategy
- `nmon.widgets.widget_base.WidgetBase`: Mock base class methods to test widget behavior
- `nmon.config.Settings`: Mock to test widget configuration loading
- `nmon.history.HistoryStore`: Mock to test widget data retrieval
- `rich.console.Console`: Mock to test widget rendering without terminal output
- `nmon.gpu_monitor.GpuMonitor`: Mock to test widget GPU data integration
- `nmon.ollama_monitor.OllamaMonitor`: Mock to test widget Ollama data integration
