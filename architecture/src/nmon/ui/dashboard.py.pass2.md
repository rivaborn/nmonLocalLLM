# src/nmon/ui/dashboard.py - Enhanced Analysis

## Architectural Role
Implements the primary dashboard UI component that aggregates and displays GPU and LLM monitoring data. Serves as the main visualization layer connecting raw metric buffers to user-facing cards and metrics.

## Cross-References
### Incoming
- `src/nmon/ui/app.py` - Initializes and manages dashboard tab lifecycle
- `src/nmon/ui/dashboard_tab.py` - Coordinates dashboard updates and data flow

### Outgoing
- `src/nmon/storage/ring_buffer.py` - Fetches GPU and LLM samples for display
- `src/nmon/gpu/monitor.py` - Accesses GPU monitoring protocols
- `src/nmon/llm/monitor.py` - Accesses LLM monitoring protocols
- `nicegui.ui` - Creates and manages UI elements

## Design Patterns
- **Observer Pattern** - Updates display asynchronously when data changes
- **Factory Pattern** - Dynamically creates GPU and LLM metric cards based on available data
- **Template Method** - Uses `_build_*` methods as structured template for UI construction
