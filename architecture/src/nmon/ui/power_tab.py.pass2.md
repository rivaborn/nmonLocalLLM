# src/nmon/ui/power_tab.py - Enhanced Analysis

## Architectural Role
PowerTab implements a time-series visualization widget for GPU power consumption within the TUI dashboard. It bridges GPU metric collection (via RingBuffer) with interactive UI rendering, serving as a configurable widget in the broader monitoring dashboard architecture.

## Cross-References
### Incoming
- `Dashboard` (in `ui/dashboard.py`) instantiates and manages PowerTab widgets
- `App` (in `ui/app.py`) routes click events to PowerTab's event handlers

### Outgoing
- `RingBuffer` (in `storage/ring_buffer.py`) for accessing GPU sample data
- `Plot` (from `textual.widgets`) for rendering time-series visualizations
- `GpuSample` (from `gpu.protocol`) for type safety in data handling

## Design Patterns
- **Observer Pattern**: Responds to mount and click events to update UI state
- **Factory Pattern**: Creates Plot widgets dynamically based on available GPU data
- **State Management**: Maintains time range selection state and updates plots accordingly
