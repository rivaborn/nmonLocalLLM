# src/nmon/widgets/sparkline.py

## Purpose
Provides a terminal-based sparkline chart widget for displaying time-series data with optional guide and threshold lines using Unicode block characters.

## Responsibilities
- Render ASCII/Unicode time-series charts in terminal
- Support multiple data series with customizable y-axis range
- Display optional horizontal guide lines and threshold markers
- Convert numerical data to visual sparkline representation
- Integrate with Rich library for terminal rendering

## Key Types
- ThresholdLine (Dataclass): Represents a horizontal threshold line with value, label, and visibility
- Sparkline (Class): Main widget class for creating and rendering sparkline charts

## Key Functions
### render
- Purpose: Converts time-series data into a Rich Panel containing Unicode sparkline chart
- Calls: None visible (uses Rich Panel constructor and Text methods)

## Globals
None

## Dependencies
- dataclasses.dataclass
- typing.List, typing.Tuple, typing.Optional
- math
- rich.panel.Panel
- rich.text.Text
