# src/nmon/views/temp_view.py - Enhanced Analysis

## Architectural Role
This file implements the temperature monitoring view component of the nmon terminal dashboard. It bridges GPU metric collection with user-facing visualization, handling both real-time rendering and interactive preference updates within the TUI's view system.

## Cross-References
### Incoming
- `src/nmon/app.py` - Calls `render_temp_view` during dashboard rendering
- `src/nmon/keyboard_handler.py` - Calls `update_temp_prefs` for user input handling

### Outgoing
- `src/nmon/history.py` - Calls `gpu_series` and `gpu_mem_series` methods
- `src/nmon/widgets/sparkline.py` - Instantiates `Sparkline` and `ThresholdLine` classes
- `src/nmon/config.py` - Accesses `UserPrefs` and `Settings` for display configuration

## Design Patterns
- **Strategy Pattern** - Uses `UserPrefs` to dynamically configure view behavior (threshold lines, memory junction display)
- **Composite Pattern** - `Layout` object composes multiple panels and sparklines into hierarchical view structure
- **Observer Pattern** - `update_temp_prefs` responds to keyboard events, updating view state in reaction to user input
